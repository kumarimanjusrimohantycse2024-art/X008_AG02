from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Application,
    Assessment,
    AssessmentStatus,
    CandidateAssessment,
    EvidenceStrength,
    Recommendation,
    Requirement,
    RequirementPriority,
)


class CandidateAssessmentError(RuntimeError):
    pass


@dataclass(frozen=True)
class CandidateAssessmentResult:
    record: CandidateAssessment
    required_coverage: dict[str, int]
    preferred_coverage: dict[str, int]
    evidence_quality: dict[str, int | str]
    strengths: list[dict[str, Any]]
    weaknesses: list[dict[str, Any]]
    tradeoffs: list[dict[str, Any]]
    recommendation: Recommendation


def _empty_coverage() -> dict[str, int]:
    return {"total": 0, "met": 0, "partially_met": 0, "unsupported": 0, "not_found": 0}


def _coverage(requirements: list[Requirement], assessments: dict[UUID, Assessment], priority: RequirementPriority) -> dict[str, int]:
    result = _empty_coverage()
    selected = [requirement for requirement in requirements if requirement.priority == priority]
    result["total"] = len(selected)
    for requirement in selected:
        status = assessments.get(requirement.id).status.value.lower() if requirement.id in assessments else "not_found"
        result[status] += 1
    return result


def _evidence_quality(requirements: list[Requirement], assessments: dict[UUID, Assessment]) -> dict[str, int | str]:
    counts = {"strong": 0, "moderate": 0, "weak": 0, "none": 0}
    for requirement in requirements:
        assessment = assessments.get(requirement.id)
        strength = assessment.evidence_strength.value.lower() if assessment else "none"
        counts[strength] += 1
    credible = counts["strong"] + counts["moderate"]
    total = sum(counts.values())
    if credible == 0:
        label = "insufficient"
    elif credible / total >= 0.75 and counts["strong"] >= counts["moderate"]:
        label = "strong"
    elif credible / total >= 0.5:
        label = "moderate"
    else:
        label = "weak"
    return {**counts, "label": label}


def _recommendation(required: dict[str, int], evidence_quality: dict[str, int | str]) -> Recommendation:
    total = required["total"]
    if total == 0:
        return Recommendation.WEAK_MATCH
    weighted = (required["met"] + required["partially_met"] * 0.5) / total
    missing = required["unsupported"] + required["not_found"]
    quality = str(evidence_quality["label"])
    if weighted == 1 and missing == 0 and quality in {"strong", "moderate"}:
        return Recommendation.STRONG_MATCH
    if weighted >= 0.8 and quality in {"strong", "moderate"}:
        return Recommendation.GOOD_MATCH
    if weighted >= 0.5 and (required["met"] > 0 or required["partially_met"] > 0):
        return Recommendation.MIXED_MATCH
    return Recommendation.WEAK_MATCH


def _source_refs(assessment: Assessment) -> list[str]:
    return [str(reference) for reference in (assessment.evidence_refs or [])]


def _narratives(requirements: list[Requirement], assessments: dict[UUID, Assessment]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    strengths: list[dict[str, Any]] = []
    weaknesses: list[dict[str, Any]] = []
    for requirement in requirements:
        assessment = assessments.get(requirement.id)
        if assessment is None:
            weaknesses.append({
                "title": f"{requirement.name} evidence not found",
                "description": f"No meaningful {requirement.name} evidence was found in the application.",
                "requirement_ids": [str(requirement.id)],
                "assessment_ids": [],
                "source_refs": [],
            })
            continue
        assessment_id = str(assessment.id)
        source_refs = _source_refs(assessment)
        if assessment.status == AssessmentStatus.MET and assessment.evidence_strength in {EvidenceStrength.STRONG, EvidenceStrength.MODERATE}:
            strengths.append({
                "title": f"{requirement.name} is supported",
                "description": assessment.evidence_summary or assessment.claim_summary or f"Verified evidence supports {requirement.name}.",
                "requirement_ids": [str(requirement.id)],
                "assessment_ids": [assessment_id],
                "source_refs": source_refs,
            })
        elif assessment.status == AssessmentStatus.NOT_FOUND:
            weaknesses.append({
                "title": f"{requirement.name} evidence not found",
                "description": f"No meaningful {requirement.name} evidence was found in the application.",
                "requirement_ids": [str(requirement.id)],
                "assessment_ids": [assessment_id],
                "source_refs": source_refs,
            })
        elif assessment.status == AssessmentStatus.UNSUPPORTED:
            weaknesses.append({
                "title": f"{requirement.name} is not sufficiently supported",
                "description": f"{requirement.name} is claimed, but the available application evidence does not support the claimed level.",
                "requirement_ids": [str(requirement.id)],
                "assessment_ids": [assessment_id],
                "source_refs": source_refs,
            })
        else:
            weaknesses.append({
                "title": f"{requirement.name} is partially supported",
                "description": f"The available evidence only partially establishes {requirement.name}.",
                "requirement_ids": [str(requirement.id)],
                "assessment_ids": [assessment_id],
                "source_refs": source_refs,
            })
        if assessment.evidence_strength in {EvidenceStrength.WEAK, EvidenceStrength.NONE} and not any(item["assessment_ids"] == [assessment_id] for item in weaknesses):
            weaknesses.append({
                "title": f"{requirement.name} evidence is weak",
                "description": f"Evidence quality for {requirement.name} is {assessment.evidence_strength.value.lower()}.",
                "requirement_ids": [str(requirement.id)],
                "assessment_ids": [assessment_id],
                "source_refs": source_refs,
            })
    return strengths, weaknesses


def _tradeoffs(strengths: list[dict[str, Any]], weaknesses: list[dict[str, Any]], requirements: dict[str, Requirement]) -> list[dict[str, Any]]:
    if not strengths or not weaknesses:
        return []
    strength = strengths[0]
    weakness = weaknesses[0]
    requirement_names = [requirements[item_id].name for item_id in strength["requirement_ids"] + weakness["requirement_ids"] if item_id in requirements]
    return [{
        "title": "Verified strength with a material evidence gap",
        "advantage": strength["description"],
        "limitation": weakness["description"],
        "requirements": requirement_names,
        "supporting_assessment_ids": strength["assessment_ids"] + weakness["assessment_ids"],
    }]


def _validate_assessments(application: Application, requirements: list[Requirement], rows: list[Assessment], assessment_ids: list[UUID] | None) -> dict[UUID, Assessment]:
    if not rows:
        raise CandidateAssessmentError("Evidence analysis required before candidate assessment.")
    requirement_map = {requirement.id: requirement for requirement in requirements}
    if assessment_ids is not None:
        requested = {str(value) for value in assessment_ids}
        rows = [row for row in rows if str(row.id) in requested]
        if len(rows) != len(requested):
            raise CandidateAssessmentError("Assessment reference does not belong to application.")
    result: dict[UUID, Assessment] = {}
    for row in rows:
        if row.application_id != application.id:
            raise CandidateAssessmentError("Assessment reference belongs to another application.")
        if row.requirement_id not in requirement_map or row.requirement.job_id != application.job_id:
            raise CandidateAssessmentError("Assessment requirement does not belong to application job.")
        result[row.requirement_id] = row
    if assessment_ids is not None and len(result) != len(requirements):
        raise CandidateAssessmentError("Candidate assessment requires the complete verified assessment set.")
    return result


def validate_candidate_assessment_output(session: Session, application_id: UUID, payload: dict[str, Any]) -> None:
    application = session.get(Application, application_id)
    if application is None:
        raise CandidateAssessmentError("Application not found.")
    requirements = session.scalars(select(Requirement).where(Requirement.job_id == application.job_id)).all()
    requirement_ids = {str(requirement.id) for requirement in requirements}
    assessments = session.scalars(select(Assessment).where(Assessment.application_id == application.id)).all()
    assessment_map = {str(assessment.id): assessment for assessment in assessments}
    referenced_assessment_ids: set[str] = set()
    referenced_requirement_ids: set[str] = set()
    for item in [*payload.get("strengths", []), *payload.get("weaknesses", [])]:
        referenced_assessment_ids.update(item.get("assessment_ids", []))
        referenced_requirement_ids.update(item.get("requirement_ids", []))
        item_assessments = [assessment_map[assessment_id] for assessment_id in item.get("assessment_ids", []) if assessment_id in assessment_map]
        item_source_refs = {reference for assessment in item_assessments for reference in (assessment.evidence_refs or [])}
        if not set(item.get("source_refs", [])).issubset(item_source_refs):
            raise CandidateAssessmentError("Narrative contains an unverified source reference.")
    for item in payload.get("tradeoffs", []):
        referenced_assessment_ids.update(item.get("supporting_assessment_ids", []))
    if not referenced_assessment_ids.issubset(assessment_map):
        raise CandidateAssessmentError("Narrative contains an assessment reference from another application.")
    if not referenced_requirement_ids.issubset(requirement_ids):
        raise CandidateAssessmentError("Narrative contains a requirement from another job.")
    if payload.get("recommendation") not in {item.value for item in Recommendation}:
        raise CandidateAssessmentError("Invalid candidate recommendation.")
    assessment_by_requirement = {assessment.requirement_id: assessment for assessment in assessments}
    expected_required = _coverage(requirements, assessment_by_requirement, RequirementPriority.REQUIRED)
    expected_preferred = _coverage(requirements, assessment_by_requirement, RequirementPriority.PREFERRED)
    expected_quality = _evidence_quality(requirements, assessment_by_requirement)
    expected_recommendation = _recommendation(expected_required, expected_quality)
    if payload.get("required_coverage") != expected_required or payload.get("preferred_coverage") != expected_preferred:
        raise CandidateAssessmentError("Candidate coverage counts do not match verified assessments.")
    if payload.get("evidence_quality") != expected_quality:
        raise CandidateAssessmentError("Evidence quality counts do not match verified assessments.")
    if payload.get("recommendation") != expected_recommendation.value:
        raise CandidateAssessmentError("Recommendation does not match deterministic policy.")


def assess_candidate(session: Session, application_id: UUID, assessment_ids: list[UUID] | None = None) -> CandidateAssessmentResult:
    application = session.get(Application, application_id)
    if application is None:
        raise CandidateAssessmentError("Application not found.")
    requirements = session.scalars(select(Requirement).where(Requirement.job_id == application.job_id).order_by(Requirement.created_at, Requirement.id)).all()
    rows = session.scalars(select(Assessment).where(Assessment.application_id == application.id).order_by(Assessment.created_at, Assessment.id)).all()
    assessments = _validate_assessments(application, requirements, rows, assessment_ids)
    required = _coverage(requirements, assessments, RequirementPriority.REQUIRED)
    preferred = _coverage(requirements, assessments, RequirementPriority.PREFERRED)
    evidence_quality = _evidence_quality(requirements, assessments)
    strengths, weaknesses = _narratives(requirements, assessments)
    requirement_map = {str(requirement.id): requirement for requirement in requirements}
    tradeoffs = _tradeoffs(strengths, weaknesses, requirement_map)
    recommendation = _recommendation(required, evidence_quality)
    validate_candidate_assessment_output(session, application.id, {
        "required_coverage": required,
        "preferred_coverage": preferred,
        "evidence_quality": evidence_quality,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "tradeoffs": tradeoffs,
        "recommendation": recommendation.value,
    })
    record = application.candidate_assessment
    if record is None:
        record = CandidateAssessment(application_id=application.id)
        session.add(record)
    record.required_coverage = required
    record.preferred_coverage = preferred
    record.evidence_quality = evidence_quality
    record.strengths = strengths
    record.weaknesses = weaknesses
    record.tradeoffs = tradeoffs
    record.recommendation = recommendation
    session.flush()
    return CandidateAssessmentResult(record, required, preferred, evidence_quality, strengths, weaknesses, tradeoffs, recommendation)