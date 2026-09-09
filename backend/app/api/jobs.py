import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_authorized_job, require_recruiter
from app.db.session import get_db
from app.models import Job, User
from app.schemas.jobs import JobCreateRequest, JobResponse

logger = logging.getLogger("talentscreen.jobs")
router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=201)
def create_job(payload: JobCreateRequest, current_user: User = Depends(require_recruiter), session: Session = Depends(get_db)) -> JobResponse:
    job = Job(**payload.model_dump(), created_by=current_user.id)
    session.add(job)
    session.flush()
    return JobResponse.model_validate(job)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: UUID, current_user: User = Depends(require_recruiter), session: Session = Depends(get_db)) -> JobResponse:
    job = get_authorized_job(job_id, current_user, session)
    return JobResponse.model_validate(job)


@router.get("", response_model=list[JobResponse])
def list_jobs(current_user: User = Depends(require_recruiter), session: Session = Depends(get_db)) -> list[JobResponse]:
    statement = select(Job) if current_user.role.value == "ADMIN" else select(Job).where(Job.created_by == current_user.id)
    return [JobResponse.model_validate(job) for job in session.scalars(statement).all()]
