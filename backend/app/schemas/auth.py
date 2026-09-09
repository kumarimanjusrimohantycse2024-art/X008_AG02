from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models import UserRole


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=1)


class AuthUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str
    role: UserRole


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AuthUser


class ProtectedResponse(BaseModel):
    message: str
    user: AuthUser
