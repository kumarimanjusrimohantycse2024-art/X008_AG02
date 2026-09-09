import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_authorized_job, require_recruiter
from app.db.session import get_db
from app.models import Job, JobStatus, Requirement, User
from app.schemas.jobs import (
    JobCreateRequest,
    JobResponse,
    JobUpdateRequest,
    RequirementAnalysisResponse,
    RequirementDraft,
    RequirementResponse,
    RequirementReviewRequest,
)
from app.services.requirement_extractor import RequirementExtractionUnavailable, extract_requirements

logger = logging.getLogger("talentscreen.jobs")
router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def serialize_job(job: Job) -> JobResponse:
    required_count = sum(requirement.priority.value == "REQUIRED" for requirement in job.requirements)
    preferred_count = sum(requirement.priority.value == "PREFERRED" for requirement in job.requirements)
    return JobResponse.model_validate({
        "id": job.id,
        "title": job.title,
        "department": job.department,
        "description": job.description,
        "status": job.status,
        "created_by": job.created_by,
        "created_at": job.created_at,
        "required_count": required_count,
        "preferred_count": preferred_count,
    })


@router.post("", response_model=JobResponse, status_code=201)
def create_job(payload: JobCreateRequest, current_user: User = Depends(require_recruiter), session: Session = Depends(get_db)) -> JobResponse:
    job = Job(**payload.model_dump(), status=JobStatus.DRAFT, created_by=current_user.id)
    session.add(job)
    session.flush()
    return serialize_job(job)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: UUID, current_user: User = Depends(require_recruiter), session: Session = Depends(get_db)) -> JobResponse:
    job = get_authorized_job(job_id, current_user, session)
    return serialize_job(job)


@router.get("", response_model=list[JobResponse])
def list_jobs(current_user: User = Depends(require_recruiter), session: Session = Depends(get_db)) -> list[JobResponse]:
    statement = select(Job) if current_user.role.value == "ADMIN" else select(Job).where(Job.created_by == current_user.id)
    return [serialize_job(job) for job in session.scalars(statement).all()]


@router.patch("/{job_id}", response_model=JobResponse)
def update_job(job_id: UUID, payload: JobUpdateRequest, current_user: User = Depends(require_recruiter), session: Session = Depends(get_db)) -> JobResponse:
    job = get_authorized_job(job_id, current_user, session)
    changes = payload.model_dump(exclude_unset=True)
    requested_status = changes.pop("status", None)
    if requested_status is not None:
        valid_transitions = {
            JobStatus.DRAFT: {JobStatus.DRAFT, JobStatus.READY},
            JobStatus.READY: {JobStatus.READY, JobStatus.ARCHIVED},
            JobStatus.SCREENING: {JobStatus.SCREENING, JobStatus.COMPLETED, JobStatus.ARCHIVED},
            JobStatus.COMPLETED: {JobStatus.COMPLETED, JobStatus.ARCHIVED},
            JobStatus.ARCHIVED: {JobStatus.ARCHIVED},
        }
        if requested_status not in valid_transitions[job.status]:
            raise HTTPException(status_code=400, detail="Invalid job status transition.")
        if requested_status == JobStatus.READY and not job.requirements:
            raise HTTPException(status_code=400, detail="A job needs finalized requirements before it is ready.")
        job.status = requested_status
    for key, value in changes.items():
        setattr(job, key, value)
    session.flush()
    return serialize_job(job)


@router.post("/{job_id}/requirements/analyze", response_model=RequirementAnalysisResponse)
def analyze_requirements(job_id: UUID, current_user: User = Depends(require_recruiter), session: Session = Depends(get_db)) -> RequirementAnalysisResponse:
    job = get_authorized_job(job_id, current_user, session)
    if not job.description.strip():
        raise HTTPException(status_code=422, detail="Job description is required for analysis.")
    try:
        result = extract_requirements(job.description)
    except RequirementExtractionUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return RequirementAnalysisResponse(requirements=result.requirements, source=result.source)


@router.put("/{job_id}/requirements", response_model=list[RequirementResponse])
def save_requirements(job_id: UUID, payload: RequirementReviewRequest, current_user: User = Depends(require_recruiter), session: Session = Depends(get_db)) -> list[RequirementResponse]:
    job = get_authorized_job(job_id, current_user, session)
    job.requirements.clear()
    job.requirements.extend(Requirement(**item.model_dump(), job_id=job.id) for item in payload.requirements)
    if not job.requirements:
        raise HTTPException(status_code=422, detail="At least one requirement is required.")
    job.status = JobStatus.READY
    session.flush()
    return [RequirementResponse.model_validate(requirement) for requirement in job.requirements]
