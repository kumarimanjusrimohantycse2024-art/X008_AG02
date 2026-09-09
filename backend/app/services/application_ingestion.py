from __future__ import annotations

import hashlib
import re
import shutil
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Application, ApplicationStatus, Document, DocumentChunk, DocumentType, IngestionStatus
from app.services.chunker import chunk_segments
from app.services.document_parser import DocumentValidationError, parse_document, validate_upload


class IngestionError(ValueError):
    pass


def storage_root() -> Path:
    root = Path(get_settings().upload_dir)
    if not root.is_absolute():
        root = Path.cwd() / root
    root.mkdir(parents=True, exist_ok=True)
    return root


def _safe_original_name(filename: str | None) -> str:
    name = Path(filename or "upload").name
    name = re.sub(r"[^A-Za-z0-9._ -]", "_", name).strip(" .")
    return name[:255] or "upload"


def _read_upload(upload, max_bytes: int) -> bytes:
    data = upload.file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise IngestionError(f"Uploaded files must be {get_settings().max_upload_size_mb} MB or smaller.")
    return data


def ingest_application_documents(session: Session, application: Application, uploads: list[tuple[object, DocumentType]]) -> int:
    settings = get_settings()
    application.ingestion_status = IngestionStatus.PROCESSING
    session.flush()
    app_dir = storage_root() / str(application.id)
    app_dir.mkdir(parents=True, exist_ok=True)
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    created_paths: list[Path] = []
    try:
        total_chunks = 0
        for upload, document_type in uploads:
            data = _read_upload(upload, max_bytes)
            validate_upload(upload.filename or "", upload.content_type, data)
            digest = hashlib.sha256(data).hexdigest()
            duplicate = session.scalar(select(Document).where(Document.application_id == application.id, Document.sha256 == digest))
            if duplicate is not None:
                raise IngestionError(f"Duplicate document upload: {_safe_original_name(upload.filename)}")
            raw_text, segments = parse_document(document_type, data)
            if not raw_text.strip():
                raise IngestionError(f"No extractable text was found in {_safe_original_name(upload.filename)}.")
            suffix = Path(upload.filename or "").suffix.lower()
            stored_path = app_dir / f"{uuid.uuid4()}{suffix}"
            stored_path.write_bytes(data)
            created_paths.append(stored_path)
            document = Document(
                application_id=application.id,
                document_type=document_type,
                file_name=_safe_original_name(upload.filename),
                mime_type=upload.content_type or "application/octet-stream",
                raw_text=raw_text,
                storage_path=str(stored_path.relative_to(Path.cwd())) if stored_path.is_relative_to(Path.cwd()) else str(stored_path.name),
                file_size=len(data),
                sha256=digest,
            )
            document.chunks = [DocumentChunk(chunk_index=chunk.chunk_index, section=chunk.section, text=chunk.text, page_number=chunk.page_number) for chunk in chunk_segments(segments)]
            session.add(document)
            session.flush()
            total_chunks += len(document.chunks)
        application.ingestion_status = IngestionStatus.COMPLETED
        application.status = ApplicationStatus.COMPLETED
        session.flush()
        return total_chunks
    except (DocumentValidationError, IngestionError) as exc:
        application.ingestion_status = IngestionStatus.FAILED
        for document in list(application.documents):
            session.delete(document)
        session.flush()
        for path in created_paths:
            path.unlink(missing_ok=True)
        raise IngestionError(str(exc)) from exc
    except Exception as exc:
        application.ingestion_status = IngestionStatus.FAILED
        for document in list(application.documents):
            session.delete(document)
        session.flush()
        for path in created_paths:
            path.unlink(missing_ok=True)
        raise IngestionError("Document processing failed.") from exc
