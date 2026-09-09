from __future__ import annotations

import logging
from collections.abc import Callable
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Application, Job, User, UserRole
from app.core.security import decode_access_token

logger = logging.getLogger("talentscreen.auth")
bearer = HTTPBearer(auto_error=False)


def unauthorized(detail: str = "Authentication required.") -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers={"WWW-Authenticate": "Bearer"})


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized()
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = UUID(str(payload["sub"]))
    except Exception:
        raise unauthorized("Invalid or expired authentication token.") from None
    user = session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise unauthorized("Invalid or expired authentication token.")
    return user


def require_roles(*roles: UserRole) -> Callable:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            logger.warning("Authorization denied for user_id=%s required_roles=%s", current_user.id, [role.value for role in roles])
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this resource.")
        return current_user
    return dependency


require_admin = require_roles(UserRole.ADMIN)
require_recruiter = require_roles(UserRole.RECRUITER, UserRole.ADMIN)


def get_authorized_job(job_id: UUID, current_user: User, session: Session) -> Job:
    job = session.scalar(select(Job).where(Job.id == job_id))
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    if current_user.role != UserRole.ADMIN and job.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return job


def get_authorized_application(application_id: UUID, current_user: User, session: Session) -> Application:
    application = session.scalar(select(Application).where(Application.id == application_id))
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")
    get_authorized_job(application.job_id, current_user, session)
    return application
