from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models import AssessmentStatus, EvidenceStrength, Recommendation, RequirementPriority


class CoverageResponse(BaseModel):
    total: int = Field(ge=0)
    met: int = Field(ge=0)
    partially_met: int = Field(ge=0)
    unsupported: int = Field(ge=0)
    not_found: int = Field(ge=0)


class EvidenceQualityResponse(BaseModel):
    label: str
    strong: int = Field(ge=0)
    moderate: int = Field(ge=0)
    weak: int = Field(ge=0)
    none: int = Field(ge=0)


class CandidateNarrativeResponse(BaseModel):
    title: str
    description: str
    requirement_ids: list[UUID]
    assessment_ids: list[UUID]
    source_refs: list[str] = []


class TradeoffResponse(BaseModel):
    title: str
    advantage: str
    limitation: str
    requirements: list[str]
    supporting_assessment_ids: list[UUID]


class RequirementAssessmentResponse(BaseModel):
    assessment_id: UUID | None
    requirement_id: UUID
    name: str
    priority: RequirementPriority
    status: AssessmentStatus
    evidence_strength: EvidenceStrength
    confidence: float | None
    claim_summary: str | None
    evidence_summary: str | None
    reasoning: str | None
    evidence_refs: list[str]


class CandidateAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    required_coverage: CoverageResponse
    preferred_coverage: CoverageResponse
    evidence_quality: EvidenceQualityResponse
    strengths: list[CandidateNarrativeResponse]
    weaknesses: list[CandidateNarrativeResponse]
    tradeoffs: list[TradeoffResponse]
    recommendation: Recommendation
    required_requirements: list[RequirementAssessmentResponse] = []
    preferred_requirements: list[RequirementAssessmentResponse] = []
    created_at: object
    updated_at: object