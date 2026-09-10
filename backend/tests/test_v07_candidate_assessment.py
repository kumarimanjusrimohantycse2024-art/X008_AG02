from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import (
    Application,
    ApplicationStatus,
    Assessment,
    AssessmentStatus,
    Candidate,
    EvidenceStrength,
    Job,
    JobStatus,
    Recommendation,
    Requirement,
    RequirementPriority,
    ScreeningStatus,
    User,
    UserRole,
)
from app.services.candidate_assessment import CandidateAssessmentError, assess_candidate
from app.services.candidate_assessment import _recommendation


def _make_candidate(session: Session, *, requirements: list[tuple[str, RequirementPriority]]) -> tuple[Application, list[Requirement]]:
    user = User(email=f"{uuid4()}@example.test", password_hash="hash", name="Recruiter", role=UserRole.RECRUITER)
    job = Job(title="Assessment job", description="Test requisition", status=JobStatus.READY, creator=user)
    job_requirements = [Requirement(name=name, description=name, priority=priority, job=job) for name, priority in requirements]
    application = Application(job=job, candidate=Candidate(name="Candidate"), status=ApplicationStatus.RECEIVED, screening_status=ScreeningStatus.NOT_STARTED)
    session.add_all([user, job, *job_requirements, application])
    session.flush()
    return application, job_requirements


def _add_assessment(
    session: Session,
    application: Application,
    requirement: Requirement,
    status: AssessmentStatus,
    strength: EvidenceStrength,
) -> Assessment:
    assessment = Assessment(
        application=application,
        requirement=requirement,
        status=status,
        evidence_strength=strength,
        confidence=Decimal("0.95"),
        claim_summary=f"Claim for {requirement.name}",
        evidence_summary=f"Evidence for {requirement.name}",
        reasoning="Verified V0.6 assessment.",
        claim_ids=[],
        evidence_refs=[],
    )
    session.add(assessment)
    session.flush()
    return assessment


def test_strong_candidate_aggregation_is_deterministic() -> None:
    session = SessionLocal()
    try:
        application, requirements = _make_candidate(session, requirements=[(f"Required {index}", RequirementPriority.REQUIRED) for index in range(5)])
        for requirement in requirements:
            _add_assessment(session, application, requirement, AssessmentStatus.MET, EvidenceStrength.STRONG)
        result = assess_candidate(session, application.id)
        assert result.required_coverage == {"total": 5, "met": 5, "partially_met": 0, "unsupported": 0, "not_found": 0}
        assert result.evidence_quality["label"] == "strong"
        assert result.recommendation == Recommendation.STRONG_MATCH
    finally:
        session.rollback()
        session.close()


def test_partial_required_gap_is_good_match_and_preferred_cannot_hide_gap() -> None:
    session = SessionLocal()
    try:
        application, requirements = _make_candidate(
            session,
            requirements=[(f"Required {index}", RequirementPriority.REQUIRED) for index in range(5)] + [("Preferred", RequirementPriority.PREFERRED)],
        )
        for index, requirement in enumerate(requirements[:5]):
            _add_assessment(session, application, requirement, AssessmentStatus.MET if index < 4 else AssessmentStatus.PARTIALLY_MET, EvidenceStrength.MODERATE)
        _add_assessment(session, application, requirements[5], AssessmentStatus.MET, EvidenceStrength.STRONG)
        result = assess_candidate(session, application.id)
        assert result.recommendation == Recommendation.GOOD_MATCH
        assert result.required_coverage["partially_met"] == 1
        assert result.preferred_coverage["met"] == 1
    finally:
        session.rollback()
        session.close()


def test_missing_and_unsupported_requirements_create_grounded_weaknesses_and_tradeoff() -> None:
    session = SessionLocal()
    try:
        application, requirements = _make_candidate(
            session,
            requirements=[("Python", RequirementPriority.REQUIRED), ("Distributed Systems", RequirementPriority.REQUIRED), ("Redis", RequirementPriority.REQUIRED)],
        )
        strong = _add_assessment(session, application, requirements[0], AssessmentStatus.MET, EvidenceStrength.STRONG)
        unsupported = _add_assessment(session, application, requirements[1], AssessmentStatus.UNSUPPORTED, EvidenceStrength.WEAK)
        missing = _add_assessment(session, application, requirements[2], AssessmentStatus.NOT_FOUND, EvidenceStrength.NONE)
        result = assess_candidate(session, application.id)
        assert result.recommendation == Recommendation.WEAK_MATCH
        assert any(item["assessment_ids"] == [str(unsupported.id)] for item in result.weaknesses)
        assert any(item["assessment_ids"] == [str(missing.id)] for item in result.weaknesses)
        assert result.tradeoffs
        assert str(strong.id) in result.tradeoffs[0]["supporting_assessment_ids"]
    finally:
        session.rollback()
        session.close()


def test_unknown_duration_remains_partial_and_not_fully_met() -> None:
    session = SessionLocal()
    try:
        application, requirements = _make_candidate(session, requirements=[("2+ years backend experience", RequirementPriority.REQUIRED)])
        _add_assessment(session, application, requirements[0], AssessmentStatus.PARTIALLY_MET, EvidenceStrength.MODERATE)
        result = assess_candidate(session, application.id)
        assert result.required_coverage["partially_met"] == 1
        assert result.recommendation != Recommendation.STRONG_MATCH
    finally:
        session.rollback()
        session.close()


def test_assessment_requires_verified_v06_rows_and_is_idempotent() -> None:
    session = SessionLocal()
    try:
        application, requirements = _make_candidate(session, requirements=[("Python", RequirementPriority.REQUIRED)])
        with pytest.raises(CandidateAssessmentError, match="Evidence analysis required"):
            assess_candidate(session, application.id)
        _add_assessment(session, application, requirements[0], AssessmentStatus.MET, EvidenceStrength.STRONG)
        first = assess_candidate(session, application.id)
        second = assess_candidate(session, application.id)
        assert first.record.id == second.record.id
    finally:
        session.rollback()
        session.close()


def test_cross_application_assessment_reference_is_rejected() -> None:
    session = SessionLocal()
    try:
        application_a, requirements_a = _make_candidate(session, requirements=[("Python", RequirementPriority.REQUIRED)])
        application_b, requirements_b = _make_candidate(session, requirements=[("Python", RequirementPriority.REQUIRED)])
        foreign = _add_assessment(session, application_b, requirements_b[0], AssessmentStatus.MET, EvidenceStrength.STRONG)
        with pytest.raises(CandidateAssessmentError, match="belongs to another application"):
            assess_candidate(session, application_a.id, assessment_ids=[foreign.id])
    finally:
        session.rollback()
        session.close()


def test_recommendation_policy_is_deterministic_and_required_first() -> None:
    quality = {"label": "strong", "strong": 5, "moderate": 0, "weak": 0, "none": 0}
    assert _recommendation({"total": 5, "met": 5, "partially_met": 0, "unsupported": 0, "not_found": 0}, quality) == Recommendation.STRONG_MATCH
    assert _recommendation({"total": 5, "met": 4, "partially_met": 1, "unsupported": 0, "not_found": 0}, quality) == Recommendation.GOOD_MATCH
    assert _recommendation({"total": 5, "met": 3, "partially_met": 1, "unsupported": 0, "not_found": 1}, quality) == Recommendation.MIXED_MATCH
    assert _recommendation({"total": 5, "met": 1, "partially_met": 0, "unsupported": 2, "not_found": 2}, quality) == Recommendation.WEAK_MATCH