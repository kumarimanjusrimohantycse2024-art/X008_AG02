from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TalentScreen API"
    app_version: str = "0.6.0"
    llm_provider: str = "local"
    llm_model: str = ""
    embedding_model: str = "local-mini"
    environment: str = "development"
    seed_user_email: str = "seed@talentscreen.local"
    seed_password_hash: str | None = Field(default=None, repr=False)
    database_url: str = "postgresql+psycopg://talentscreen:talentscreen@localhost:5434/talentscreen"
    embedding_dimension: int = 1536
    jwt_secret: str = Field(default="development-only-change-me-32-characters", repr=False)
    access_token_expire_minutes: int = 60
    password_min_length: int = 8
    llm_api_key: str | None = Field(default=None, repr=False)
    embedding_api_key: str | None = Field(default=None, repr=False)
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    demo_mode: bool = False

    demo_admin_email: str | None = None
    demo_admin_password: str | None = Field(default=None, repr=False)
    demo_recruiter_email: str | None = None
    demo_recruiter_password: str | None = Field(default=None, repr=False)
    upload_dir: str = "storage/uploads"
    max_upload_size_mb: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
