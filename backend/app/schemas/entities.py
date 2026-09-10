from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models import (
    ApplicationStatus, AssessmentStatus, ClaimType, DocumentType, EvidenceStrength, EvidenceType,
    GapLevel, JobStatus, LinkRelationship, Recommendation, RequirementPriority, ScreeningStatus,
    UserRole,
)


class EntitySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(EntitySchema):
    id: UUID
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    email: str
    password_hash: str = Field(min_length=1)
    name: str
    role: UserRole


class UserRead(TimestampSchema):
    email: str
    name: str
    role: UserRole


class JobCreate(BaseModel):
    title: str
    department: str | None = None
    description: str
    status: JobStatus = JobStatus.DRAFT
    created_by: UUID


class JobRead(TimestampSchema):
    title: str
    department: str | None
    description: str
    status: JobStatus
    created_by: UUID


class JobUpdate(BaseModel):
    title: str | None = None
    department: str | None = None
    description: str | None = None
    status: JobStatus | None = None


class RequirementCreate(BaseModel):
    job_id: UUID
    name: str
    description: str | None = None
    priority: RequirementPriority
    minimum_years: Decimal | None = Field(default=None, ge=0)
    weight: Decimal = Field(default=1, ge=0)
    aliases: list[str] = Field(default_factory=list)
    evidence_expectations: dict[str, Any] = Field(default_factory=dict)


class RequirementRead(TimestampSchema):
    job_id: UUID
    name: str
    description: str | None
    priority: RequirementPriority
    minimum_years: Decimal | None
    weight: Decimal
    aliases: list[str]
    evidence_expectations: dict[str, Any]


class CandidateCreate(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None


class CandidateRead(TimestampSchema):
    name: str
    email: str | None
    phone: str | None


class ApplicationCreate(BaseModel):
    job_id: UUID
    candidate_id: UUID
    status: ApplicationStatus = ApplicationStatus.RECEIVED
    screening_status: ScreeningStatus = ScreeningStatus.NOT_STARTED
    submitted_at: datetime | None = None


class ApplicationRead(TimestampSchema):
    job_id: UUID
    candidate_id: UUID
    status: ApplicationStatus
    screening_status: ScreeningStatus
    submitted_at: datetime | None


class DocumentCreate(BaseModel):
    application_id: UUID
    document_type: DocumentType
    file_name: str
    mime_type: str
    raw_text: str | None = None


class DocumentRead(TimestampSchema):
    application_id: UUID
    document_type: DocumentType
    file_name: str
    mime_type: str
    raw_text: str | None


class DocumentChunkCreate(BaseModel):
    document_id: UUID
    chunk_index: int = Field(ge=0)
    section: str | None = None
    text: str
    page_number: int | None = Field(default=None, ge=1)
    embedding: list[float] | None = None


class DocumentChunkRead(EntitySchema):
    id: UUID
    document_id: UUID
    chunk_index: int
    section: str | None
    text: str
    page_number: int | None
    embedding: list[float] | None
    created_at: datetime


class ClaimCreate(BaseModel):
    application_id: UUID
    text: str
    claim_type: ClaimType
    source_chunk_id: UUID | None = None


class ClaimRead(EntitySchema):
    id: UUID
    application_id: UUID
    text: str
    claim_type: ClaimType
    source_chunk_id: UUID | None
    created_at: datetime


class ClaimRequirementLinkCreate(BaseModel):
    claim_id: UUID
    requirement_id: UUID
    relationship: LinkRelationship
    similarity: Decimal | None = Field(default=None, ge=0, le=1)


class ClaimRequirementLinkRead(EntitySchema):
    id: UUID
    claim_id: UUID
    requirement_id: UUID
    relationship: LinkRelationship
    similarity: Decimal | None
    created_at: datetime


class EvidenceCreate(BaseModel):
    application_id: UUID
    claim_id: UUID | None = None
    requirement_id: UUID | None = None
    text: str
    source_chunk_id: UUID
    evidence_type: EvidenceType


class EvidenceRead(EntitySchema):
    id: UUID
    application_id: UUID
    claim_id: UUID | None
    requirement_id: UUID | None
    text: str
    source_chunk_id: UUID
    evidence_type: EvidenceType
    created_at: datetime


class AssessmentCreate(BaseModel):
    application_id: UUID
    requirement_id: UUID
    status: AssessmentStatus
    evidence_strength: EvidenceStrength
    confidence: Decimal = Field(ge=0, le=1)
    claim_summary: str | None = None
    evidence_summary: str | None = None
    reasoning: str | None = None


class AssessmentRead(TimestampSchema):
    application_id: UUID
    requirement_id: UUID
    status: AssessmentStatus
    evidence_strength: EvidenceStrength
    confidence: Decimal
    claim_summary: str | None
    evidence_summary: str | None
    reasoning: str | None


class CandidateAssessmentCreate(BaseModel):
    application_id: UUID
    required_coverage: dict[str, Any] = Field(default_factory=dict)
    preferred_coverage: dict[str, Any] = Field(default_factory=dict)
    evidence_quality: dict[str, Any] = Field(default_factory=dict)
    strengths: list[Any] = Field(default_factory=list)
    weaknesses: list[Any] = Field(default_factory=list)
    tradeoffs: list[Any] = Field(default_factory=list)
    recommendation: Recommendation


class CandidateAssessmentRead(TimestampSchema):
    application_id: UUID
    required_coverage: dict[str, Any]
    preferred_coverage: dict[str, Any]
    evidence_quality: dict[str, Any]
    strengths: list[Any]
    weaknesses: list[Any]
    tradeoffs: list[Any]
    recommendation: Recommendation


class CandidateRankingCreate(BaseModel):
    job_id: UUID
    application_id: UUID
    rank: int = Field(gt=0)
    ranking_signal: dict[str, Any] = Field(default_factory=dict)
    summary: str | None = None
    tradeoffs: list[Any] = Field(default_factory=list)


class CandidateRankingRead(EntitySchema):
    id: UUID
    job_id: UUID
    application_id: UUID
    rank: int
    ranking_signal: dict[str, Any]
    summary: str | None
    tradeoffs: list[Any]
    created_at: datetime


class PoolGapCreate(BaseModel):
    job_id: UUID
    requirement_id: UUID
    candidate_count: int = Field(default=0, ge=0)
    strong_count: int = Field(default=0, ge=0)
    moderate_count: int = Field(default=0, ge=0)
    weak_count: int = Field(default=0, ge=0)
    unsupported_count: int = Field(default=0, ge=0)
    not_found_count: int = Field(default=0, ge=0)
    coverage_rate: Decimal = Field(default=0, ge=0, le=1)
    gap_level: GapLevel
    explanation: str | None = None


class PoolGapRead(TimestampSchema):
    job_id: UUID
    requirement_id: UUID
    candidate_count: int
    strong_count: int
    moderate_count: int
    weak_count: int
    unsupported_count: int
    not_found_count: int
    coverage_rate: Decimal
    gap_level: GapLevel
    explanation: str | None
