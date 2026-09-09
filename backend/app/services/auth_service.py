from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models import User


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    user = session.scalar(select(User).where(User.email == email.strip().lower()))
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user
