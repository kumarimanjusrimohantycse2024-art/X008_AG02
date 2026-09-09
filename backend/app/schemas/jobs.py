from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models import JobStatus


class JobCreateRequest(BaseModel):
    title: str
    department: str | None = None
    description: str
    status: JobStatus = JobStatus.DRAFT


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    department: str | None
    description: str
    status: JobStatus
    created_by: UUID
