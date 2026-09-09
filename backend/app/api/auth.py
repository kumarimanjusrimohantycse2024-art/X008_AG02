import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.models import User
from app.schemas.auth import AuthUser, LoginRequest, LoginResponse, ProtectedResponse
from app.services.auth_service import authenticate_user

logger = logging.getLogger("talentscreen.auth")
router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, session: Session = Depends(get_db)) -> LoginResponse:
    user = authenticate_user(session, payload.email, payload.password)
    if user is None:
        logger.warning("Login failed for email=%s", payload.email.strip().lower())
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.", headers={"WWW-Authenticate": "Bearer"})
    token, expires_in = create_access_token(user.id, user.role.value)
    logger.info("Login succeeded for user_id=%s", user.id)
    return LoginResponse(access_token=token, expires_in=expires_in, user=AuthUser.model_validate(user))


@router.get("/me", response_model=AuthUser)
def me(current_user: User = Depends(get_current_user)) -> AuthUser:
    return AuthUser.model_validate(current_user)


@router.get("/protected", response_model=ProtectedResponse)
def protected(current_user: User = Depends(get_current_user)) -> ProtectedResponse:
    return ProtectedResponse(message="Authenticated access granted.", user=AuthUser.model_validate(current_user))
