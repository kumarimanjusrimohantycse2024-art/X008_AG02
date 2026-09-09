from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    Application,
    ApplicationStatus,
    Candidate,
    Claim,
    ClaimType,
    Document,
    DocumentChunk,
    DocumentType,
    Evidence,
    EvidenceStrength,
    EvidenceType,
    Job,
    JobStatus,
    Requirement,
    RequirementPriority,
    ScreeningStatus,
    User,
    UserRole,
)
from app.schemas.entities import AssessmentCreate, PoolGapCreate


def make_job_graph(session: Session) -> tuple[User, Job, Requirement, Candidate, Application, Document, DocumentChunk]:
    user = User(email=f"{uuid4()}@example.test", password_hash="hash", name="Test User", role=UserRole.RECRUITER)
    job = Job(title="Test Job", description="Test description", status=JobStatus.DRAFT, creator=user)
    requirement = Requirement(name="Python", priority=RequirementPriority.REQUIRED, job=job)
    candidate = Candidate(name="Test Candidate")
    application = Application(job=job, candidate=candidate, status=ApplicationStatus.RECEIVED, screening_status=ScreeningStatus.NOT_STARTED)
    document = Document(application=application, document_type=DocumentType.RESUME, file_name="resume.txt", mime_type="text/plain", raw_text="Python")
    chunk = DocumentChunk(document=document, chunk_index=0, text="Python")
    session.add(user)
    session.flush()
    return user, job, requirement, candidate, application, document, chunk


def test_relationship_graph_and_uuid_ids(db_session: Session) -> None:
    user, job, requirement, candidate, application, document, chunk = make_job_graph(db_session)
    assert user.id is not None and job.id is not None and application.id is not None
    assert job.creator is user
    assert job.requirements == [requirement]
    assert job.applications == [application]
    assert candidate.applications == [application]
    assert application.documents == [document]
    assert document.chunks == [chunk]


def test_claim_and_evidence_preserve_source_chunk(db_session: Session) -> None:
    _, _, requirement, _, application, _, chunk = make_job_graph(db_session)
    claim = Claim(application=application, text="Built Python services", claim_type=ClaimType.EXPERIENCE, source_chunk=chunk)
    evidence = Evidence(application=application, claim=claim, requirement=requirement, text="Built Python services", source_chunk=chunk, evidence_type=EvidenceType.PROFESSIONAL)
    db_session.add_all([claim, evidence])
    db_session.flush()
    assert claim.source_chunk_id == chunk.id
    assert evidence.source_chunk_id == chunk.id
    assert evidence.application_id == application.id


def test_database_constraints_reject_invalid_values(db_session: Session) -> None:
    user = User(email=f"{uuid4()}@example.test", password_hash="hash", name="Test", role=UserRole.RECRUITER)
    db_session.add(user)
    db_session.flush()
    duplicate = User(email=user.email, password_hash="hash", name="Duplicate", role=UserRole.RECRUITER)
    db_session.add(duplicate)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    assessment = AssessmentCreate(application_id=uuid4(), requirement_id=uuid4(), status="MET", evidence_strength="STRONG", confidence=Decimal("0.8"))
    assert assessment.confidence == Decimal("0.8")
    with pytest.raises(ValidationError):
        AssessmentCreate(application_id=uuid4(), requirement_id=uuid4(), status="MET", evidence_strength="STRONG", confidence=Decimal("1.1"))
    with pytest.raises(ValidationError):
        PoolGapCreate(job_id=uuid4(), requirement_id=uuid4(), gap_level="LOW", candidate_count=-1)


def test_application_cascade_removes_documents_and_claims(db_session: Session) -> None:
    _, job, _, _, application, document, chunk = make_job_graph(db_session)
    claim = Claim(application=application, text="Python", claim_type=ClaimType.SKILL, source_chunk=chunk)
    db_session.add(claim)
    db_session.flush()
    db_session.delete(application)
    db_session.flush()
    assert db_session.scalar(select(Document).where(Document.id == document.id)) is None
    assert db_session.scalar(select(DocumentChunk).where(DocumentChunk.id == chunk.id)) is None
    assert db_session.scalar(select(Claim).where(Claim.id == claim.id)) is None
    assert db_session.scalar(select(Job).where(Job.id == job.id)) is not None
