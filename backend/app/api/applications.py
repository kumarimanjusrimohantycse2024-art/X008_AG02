from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_authorized_application, get_authorized_job, require_recruiter
from app.db.session import get_db
from app.models import Application, ApplicationStatus, Candidate, Document, DocumentChunk, DocumentType, IngestionStatus, ScreeningStatus, User
from app.schemas.applications import ApplicationDetailResponse, ApplicationResponse, ChunkResponse, DocumentResponse
from app.services.application_ingestion import IngestionError, ingest_application_documents

logger = logging.getLogger("talentscreen.applications")
router = APIRouter(prefix="/api", tags=["applications"])


def serialize_document(document: Document) -> DocumentResponse:
    return DocumentResponse.model_validate({**document.__dict__, "chunk_count": len(document.chunks)})


def serialize_application(application: Application) -> ApplicationResponse:
    return ApplicationResponse.model_validate({
        **application.__dict__,
        "candidate_name": application.candidate.name,
        "candidate_email": application.candidate.email,
        "candidate_phone": application.candidate.phone,
        "document_count": len(application.documents),
        "chunk_count": sum(len(document.chunks) for document in application.documents),
    })


@router.post("/jobs/{job_id}/applications", response_model=ApplicationDetailResponse, status_code=201)
def create_application(
    job_id: UUID,
    candidate_name: str = Form(...),
    candidate_email: str | None = Form(default=None),
    candidate_phone: str | None = Form(default=None),
    resume: UploadFile = File(...),
    cover_letter: UploadFile | None = File(default=None),
    current_user: User = Depends(require_recruiter),
    session: Session = Depends(get_db),
) -> ApplicationDetailResponse:
    job = get_authorized_job(job_id, current_user, session)
    if not candidate_name.strip():
        raise HTTPException(status_code=422, detail="Candidate name is required.")
    if candidate_email:
        candidate_email = candidate_email.strip().lower() or None
    candidate = Candidate(name=candidate_name.strip(), email=candidate_email, phone=candidate_phone.strip() if candidate_phone else None)
    application = Application(
        job=job,
        candidate=candidate,
        status=ApplicationStatus.RECEIVED,
        ingestion_status=IngestionStatus.NOT_STARTED,
        screening_status=ScreeningStatus.NOT_STARTED,
        submitted_at=datetime.now(timezone.utc),
    )
    session.add(application)
    session.flush()
    uploads = [(resume, DocumentType.RESUME)]
    if cover_letter is not None:
        uploads.append((cover_letter, DocumentType.COVER_LETTER))
    try:
        ingest_application_documents(session, application, uploads)
        session.flush()
        return ApplicationDetailResponse.model_validate({**serialize_application(application).model_dump(), "documents": [serialize_document(document) for document in application.documents]})
    except IngestionError as exc:
        session.commit()
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/jobs/{job_id}/applications", response_model=list[ApplicationResponse])
def list_applications(job_id: UUID, current_user: User = Depends(require_recruiter), session: Session = Depends(get_db)) -> list[ApplicationResponse]:
    get_authorized_job(job_id, current_user, session)
    applications = session.scalars(select(Application).where(Application.job_id == job_id).order_by(Application.created_at.desc())).all()
    return [serialize_application(application) for application in applications]


@router.get("/applications/{application_id}", response_model=ApplicationDetailResponse)
def get_application(application_id: UUID, current_user: User = Depends(require_recruiter), session: Session = Depends(get_db)) -> ApplicationDetailResponse:
    application = get_authorized_application(application_id, current_user, session)
    return ApplicationDetailResponse.model_validate({**serialize_application(application).model_dump(), "documents": [serialize_document(document) for document in application.documents]})


@router.get("/applications/{application_id}/documents", response_model=list[DocumentResponse])
def list_documents(application_id: UUID, current_user: User = Depends(require_recruiter), session: Session = Depends(get_db)) -> list[DocumentResponse]:
    application = get_authorized_application(application_id, current_user, session)
    return [serialize_document(document) for document in application.documents]


@router.get("/applications/{application_id}/documents/{document_id}", response_model=DocumentResponse)
def get_document(application_id: UUID, document_id: UUID, current_user: User = Depends(require_recruiter), session: Session = Depends(get_db)) -> DocumentResponse:
    application = get_authorized_application(application_id, current_user, session)
    document = session.scalar(select(Document).where(Document.id == document_id, Document.application_id == application.id))
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return serialize_document(document)


@router.get("/applications/{application_id}/chunks", response_model=list[ChunkResponse])
def list_chunks(application_id: UUID, current_user: User = Depends(require_recruiter), session: Session = Depends(get_db)) -> list[ChunkResponse]:
    application = get_authorized_application(application_id, current_user, session)
    chunks = session.scalars(select(DocumentChunk).join(Document).where(Document.application_id == application.id).order_by(DocumentChunk.document_id, DocumentChunk.chunk_index)).all()
    return [ChunkResponse.model_validate(chunk) for chunk in chunks]
