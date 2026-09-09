from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models import ApplicationStatus, DocumentType, IngestionStatus, ScreeningStatus


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_type: DocumentType
    file_name: str
    mime_type: str
    file_size: int
    sha256: str
    raw_text: str | None
    created_at: datetime
    chunk_count: int = 0


class ChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    chunk_index: int
    section: str | None
    text: str
    page_number: int | None
    created_at: datetime


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    candidate_id: UUID
    candidate_name: str
    candidate_email: str | None
    candidate_phone: str | None
    status: ApplicationStatus
    ingestion_status: IngestionStatus
    screening_status: ScreeningStatus
    submitted_at: datetime | None
    created_at: datetime
    document_count: int = 0
    chunk_count: int = 0


class ApplicationDetailResponse(ApplicationResponse):
    documents: list[DocumentResponse]
