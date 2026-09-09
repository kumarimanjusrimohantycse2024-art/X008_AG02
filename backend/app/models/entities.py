from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    UUID,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import get_settings
from app.db.base import Base


class StrEnum(str, enum.Enum):
    pass


class UserRole(StrEnum):
    ADMIN = "ADMIN"
    RECRUITER = "RECRUITER"


class JobStatus(StrEnum):
    DRAFT = "DRAFT"
    READY = "READY"
    SCREENING = "SCREENING"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class RequirementPriority(StrEnum):
    REQUIRED = "REQUIRED"
    PREFERRED = "PREFERRED"


class ApplicationStatus(StrEnum):
    RECEIVED = "RECEIVED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ScreeningStatus(StrEnum):
    NOT_STARTED = "NOT_STARTED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class IngestionStatus(StrEnum):
    NOT_STARTED = "NOT_STARTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DocumentType(StrEnum):
    RESUME = "RESUME"
    COVER_LETTER = "COVER_LETTER"
    OTHER = "OTHER"


class ClaimType(StrEnum):
    SKILL = "SKILL"
    EXPERIENCE = "EXPERIENCE"
    EDUCATION = "EDUCATION"
    CERTIFICATION = "CERTIFICATION"
    PROJECT = "PROJECT"
    RESPONSIBILITY = "RESPONSIBILITY"
    OTHER = "OTHER"


class LinkRelationship(StrEnum):
    DIRECT = "DIRECT"
    EQUIVALENT = "EQUIVALENT"
    RELATED = "RELATED"
    WEAKLY_RELATED = "WEAKLY_RELATED"


class EvidenceType(StrEnum):
    DIRECT = "DIRECT"
    INDIRECT = "INDIRECT"
    PROJECT = "PROJECT"
    PROFESSIONAL = "PROFESSIONAL"
    ACADEMIC = "ACADEMIC"
    CERTIFICATION = "CERTIFICATION"
    OTHER = "OTHER"


class AssessmentStatus(StrEnum):
    MET = "MET"
    PARTIALLY_MET = "PARTIALLY_MET"
    UNSUPPORTED = "UNSUPPORTED"
    NOT_FOUND = "NOT_FOUND"


class EvidenceStrength(StrEnum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    NONE = "NONE"


class Recommendation(StrEnum):
    STRONG_MATCH = "STRONG_MATCH"
    GOOD_MATCH = "GOOD_MATCH"
    MIXED_MATCH = "MIXED_MATCH"
    WEAK_MATCH = "WEAK_MATCH"


class GapLevel(StrEnum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


def enum_type(enum_class: type[StrEnum]) -> Enum:
    return Enum(enum_class, name=enum_class.__name__.lower(), native_enum=True, create_constraint=True)


def uuid_column(**kwargs: Any) -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, **kwargs)


def timestamps() -> dict[str, Any]:
    return {
        "created_at": mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False),
        "updated_at": mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
    }


class User(Base):
    __tablename__ = "users"
    __table_args__ = (Index("ix_users_email", "email"),)

    id: Mapped[uuid.UUID] = uuid_column()
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[UserRole] = mapped_column(enum_type(UserRole), nullable=False)
    created_at: Mapped[datetime] = timestamps()["created_at"]
    updated_at: Mapped[datetime] = timestamps()["updated_at"]

    jobs: Mapped[list[Job]] = relationship(back_populates="creator")


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (Index("ix_jobs_created_by", "created_by"), Index("ix_jobs_status", "status"))

    id: Mapped[uuid.UUID] = uuid_column()
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[str | None] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[JobStatus] = mapped_column(enum_type(JobStatus), nullable=False, default=JobStatus.DRAFT)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = timestamps()["created_at"]
    updated_at: Mapped[datetime] = timestamps()["updated_at"]

    creator: Mapped[User] = relationship(back_populates="jobs")
    requirements: Mapped[list[Requirement]] = relationship(back_populates="job", cascade="all, delete-orphan")
    applications: Mapped[list[Application]] = relationship(back_populates="job", cascade="all, delete-orphan")
    rankings: Mapped[list[CandidateRanking]] = relationship(back_populates="job", cascade="all, delete-orphan")
    pool_gaps: Mapped[list[PoolGap]] = relationship(back_populates="job", cascade="all, delete-orphan")


class Requirement(Base):
    __tablename__ = "requirements"
    __table_args__ = (Index("ix_requirements_job_id", "job_id"),)

    id: Mapped[uuid.UUID] = uuid_column()
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[RequirementPriority] = mapped_column(enum_type(RequirementPriority), nullable=False)
    minimum_years: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    weight: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False, default=1)
    aliases: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    evidence_expectations: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = timestamps()["created_at"]
    updated_at: Mapped[datetime] = timestamps()["updated_at"]

    job: Mapped[Job] = relationship(back_populates="requirements")
    claim_links: Mapped[list[ClaimRequirementLink]] = relationship(back_populates="requirement", cascade="all, delete-orphan")
    assessments: Mapped[list[Assessment]] = relationship(back_populates="requirement", cascade="all, delete-orphan")
    pool_gaps: Mapped[list[PoolGap]] = relationship(back_populates="requirement", cascade="all, delete-orphan")
    evidence: Mapped[list[Evidence]] = relationship(back_populates="requirement")


class Candidate(Base):
    __tablename__ = "candidates"
    __table_args__ = (Index("ix_candidates_email", "email"),)

    id: Mapped[uuid.UUID] = uuid_column()
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320))
    phone: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = timestamps()["created_at"]
    updated_at: Mapped[datetime] = timestamps()["updated_at"]

    applications: Mapped[list[Application]] = relationship(back_populates="candidate")


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        Index("ix_applications_job_id", "job_id"),
        Index("ix_applications_candidate_id", "candidate_id"),
        Index("ix_applications_screening_status", "screening_status"),
        Index("ix_applications_ingestion_status", "ingestion_status"),
    )

    id: Mapped[uuid.UUID] = uuid_column()
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    candidate_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("candidates.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(enum_type(ApplicationStatus), nullable=False, default=ApplicationStatus.RECEIVED)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    screening_status: Mapped[ScreeningStatus] = mapped_column(enum_type(ScreeningStatus), nullable=False, default=ScreeningStatus.NOT_STARTED)
    ingestion_status: Mapped[IngestionStatus] = mapped_column(enum_type(IngestionStatus), nullable=False, default=IngestionStatus.NOT_STARTED)
    created_at: Mapped[datetime] = timestamps()["created_at"]
    updated_at: Mapped[datetime] = timestamps()["updated_at"]

    job: Mapped[Job] = relationship(back_populates="applications")
    candidate: Mapped[Candidate] = relationship(back_populates="applications")
    documents: Mapped[list[Document]] = relationship(back_populates="application", cascade="all, delete-orphan")
    claims: Mapped[list[Claim]] = relationship(back_populates="application", cascade="all, delete-orphan")
    evidence: Mapped[list[Evidence]] = relationship(back_populates="application", cascade="all, delete-orphan")
    assessments: Mapped[list[Assessment]] = relationship(back_populates="application", cascade="all, delete-orphan")
    candidate_assessment: Mapped[CandidateAssessment | None] = relationship(back_populates="application", cascade="all, delete-orphan", uselist=False)


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (Index("ix_documents_application_id", "application_id"),)

    id: Mapped[uuid.UUID] = uuid_column()
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    document_type: Mapped[DocumentType] = mapped_column(enum_type(DocumentType), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(150), nullable=False)
    raw_text: Mapped[str | None] = mapped_column(Text)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    created_at: Mapped[datetime] = timestamps()["created_at"]
    updated_at: Mapped[datetime] = timestamps()["updated_at"]

    application: Mapped[Application] = relationship(back_populates="documents")
    chunks: Mapped[list[DocumentChunk]] = relationship(back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (
        Index("ix_document_chunks_document_id", "document_id"),
        Index("ix_document_chunks_document_chunk_index", "document_id", "chunk_index"),
        CheckConstraint("chunk_index >= 0", name="ck_document_chunks_chunk_index_nonnegative"),
    )

    id: Mapped[uuid.UUID] = uuid_column()
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    section: Mapped[str | None] = mapped_column(String(200))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(get_settings().embedding_dimension))
    created_at: Mapped[datetime] = timestamps()["created_at"]

    document: Mapped[Document] = relationship(back_populates="chunks")


class Claim(Base):
    __tablename__ = "claims"
    __table_args__ = (Index("ix_claims_application_id", "application_id"), Index("ix_claims_source_chunk_id", "source_chunk_id"))

    id: Mapped[uuid.UUID] = uuid_column()
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    claim_type: Mapped[ClaimType] = mapped_column(enum_type(ClaimType), nullable=False)
    source_chunk_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("document_chunks.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = timestamps()["created_at"]

    application: Mapped[Application] = relationship(back_populates="claims")
    source_chunk: Mapped[DocumentChunk | None] = relationship()
    claim_requirement_links: Mapped[list[ClaimRequirementLink]] = relationship(back_populates="claim", cascade="all, delete-orphan")
    evidence: Mapped[list[Evidence]] = relationship(back_populates="claim")


class ClaimRequirementLink(Base):
    __tablename__ = "claim_requirement_links"
    __table_args__ = (
        UniqueConstraint("claim_id", "requirement_id", name="uq_claim_requirement_links_claim_requirement"),
        Index("ix_claim_requirement_links_claim_id", "claim_id"),
        Index("ix_claim_requirement_links_requirement_id", "requirement_id"),
        CheckConstraint("similarity IS NULL OR (similarity >= 0 AND similarity <= 1)", name="ck_claim_requirement_links_similarity_range"),
    )

    id: Mapped[uuid.UUID] = uuid_column()
    claim_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    requirement_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False)
    link_relationship: Mapped[LinkRelationship] = mapped_column("relationship", enum_type(LinkRelationship), nullable=False)
    similarity: Mapped[Decimal | None] = mapped_column(Numeric(6, 5))
    created_at: Mapped[datetime] = timestamps()["created_at"]

    claim: Mapped[Claim] = relationship(back_populates="claim_requirement_links")
    requirement: Mapped[Requirement] = relationship(back_populates="claim_links")


class Evidence(Base):
    __tablename__ = "evidence"
    __table_args__ = (
        Index("ix_evidence_application_id", "application_id"),
        Index("ix_evidence_requirement_id", "requirement_id"),
        Index("ix_evidence_source_chunk_id", "source_chunk_id"),
    )

    id: Mapped[uuid.UUID] = uuid_column()
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    claim_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("claims.id", ondelete="SET NULL"))
    requirement_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("requirements.id", ondelete="SET NULL"))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source_chunk_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("document_chunks.id", ondelete="RESTRICT"), nullable=False)
    evidence_type: Mapped[EvidenceType] = mapped_column(enum_type(EvidenceType), nullable=False)
    created_at: Mapped[datetime] = timestamps()["created_at"]

    application: Mapped[Application] = relationship(back_populates="evidence")
    claim: Mapped[Claim | None] = relationship(back_populates="evidence")
    requirement: Mapped[Requirement | None] = relationship(back_populates="evidence")
    source_chunk: Mapped[DocumentChunk] = relationship()


class Assessment(Base):
    __tablename__ = "assessments"
    __table_args__ = (
        UniqueConstraint("application_id", "requirement_id", name="uq_assessments_application_requirement"),
        Index("ix_assessments_application_id", "application_id"),
        Index("ix_assessments_requirement_id", "requirement_id"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_assessments_confidence_range"),
    )

    id: Mapped[uuid.UUID] = uuid_column()
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    requirement_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[AssessmentStatus] = mapped_column(enum_type(AssessmentStatus), nullable=False)
    evidence_strength: Mapped[EvidenceStrength] = mapped_column(enum_type(EvidenceStrength), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False)
    claim_summary: Mapped[str | None] = mapped_column(Text)
    evidence_summary: Mapped[str | None] = mapped_column(Text)
    reasoning: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = timestamps()["created_at"]
    updated_at: Mapped[datetime] = timestamps()["updated_at"]

    application: Mapped[Application] = relationship(back_populates="assessments")
    requirement: Mapped[Requirement] = relationship(back_populates="assessments")


class CandidateAssessment(Base):
    __tablename__ = "candidate_assessments"
    __table_args__ = (
        UniqueConstraint("application_id", name="uq_candidate_assessments_application"),
        Index("ix_candidate_assessments_application_id", "application_id"),
        CheckConstraint("required_coverage >= 0 AND required_coverage <= 1", name="ck_candidate_assessments_required_coverage_range"),
        CheckConstraint("preferred_coverage >= 0 AND preferred_coverage <= 1", name="ck_candidate_assessments_preferred_coverage_range"),
        CheckConstraint("evidence_quality >= 0 AND evidence_quality <= 1", name="ck_candidate_assessments_evidence_quality_range"),
    )

    id: Mapped[uuid.UUID] = uuid_column()
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    required_coverage: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False)
    preferred_coverage: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False)
    evidence_quality: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False)
    strengths: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    weaknesses: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    tradeoffs: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    recommendation: Mapped[Recommendation] = mapped_column(enum_type(Recommendation), nullable=False)
    created_at: Mapped[datetime] = timestamps()["created_at"]
    updated_at: Mapped[datetime] = timestamps()["updated_at"]

    application: Mapped[Application] = relationship(back_populates="candidate_assessment")


class CandidateRanking(Base):
    __tablename__ = "candidate_rankings"
    __table_args__ = (
        UniqueConstraint("job_id", "application_id", name="uq_candidate_rankings_job_application"),
        Index("ix_candidate_rankings_job_id", "job_id"),
        Index("ix_candidate_rankings_job_rank", "job_id", "rank"),
        CheckConstraint("rank > 0", name="ck_candidate_rankings_rank_positive"),
    )

    id: Mapped[uuid.UUID] = uuid_column()
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    ranking_signal: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    summary: Mapped[str | None] = mapped_column(Text)
    tradeoffs: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = timestamps()["created_at"]

    job: Mapped[Job] = relationship(back_populates="rankings")
    application: Mapped[Application] = relationship()


class PoolGap(Base):
    __tablename__ = "pool_gaps"
    __table_args__ = (
        UniqueConstraint("job_id", "requirement_id", name="uq_pool_gaps_job_requirement"),
        Index("ix_pool_gaps_job_id", "job_id"),
        Index("ix_pool_gaps_requirement_id", "requirement_id"),
        CheckConstraint("candidate_count >= 0", name="ck_pool_gaps_candidate_count_nonnegative"),
        CheckConstraint("strong_count >= 0", name="ck_pool_gaps_strong_count_nonnegative"),
        CheckConstraint("moderate_count >= 0", name="ck_pool_gaps_moderate_count_nonnegative"),
        CheckConstraint("weak_count >= 0", name="ck_pool_gaps_weak_count_nonnegative"),
        CheckConstraint("unsupported_count >= 0", name="ck_pool_gaps_unsupported_count_nonnegative"),
        CheckConstraint("not_found_count >= 0", name="ck_pool_gaps_not_found_count_nonnegative"),
        CheckConstraint("coverage_rate >= 0 AND coverage_rate <= 1", name="ck_pool_gaps_coverage_rate_range"),
    )

    id: Mapped[uuid.UUID] = uuid_column()
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    requirement_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False)
    candidate_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    strong_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    moderate_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    weak_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unsupported_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    not_found_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    coverage_rate: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False, default=0)
    gap_level: Mapped[GapLevel] = mapped_column(enum_type(GapLevel), nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = timestamps()["created_at"]
    updated_at: Mapped[datetime] = timestamps()["updated_at"]

    job: Mapped[Job] = relationship(back_populates="pool_gaps")
    requirement: Mapped[Requirement] = relationship(back_populates="pool_gaps")
