from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin
from app.db.session import get_db
from app.models import User
from app.schemas.auth import AuthUser

router = APIRouter(prefix="/api/admin", tags=["administration"])


@router.get("/users", response_model=list[AuthUser])
def list_users(current_user: User = Depends(require_admin), session: Session = Depends(get_db)) -> list[AuthUser]:
    users = session.scalars(select(User).order_by(User.created_at)).all()
    return [AuthUser.model_validate(user) for user in users]
