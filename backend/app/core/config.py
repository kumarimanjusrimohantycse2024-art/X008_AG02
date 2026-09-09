from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TalentScreen API"
    app_version: str = "0.1.0"
    database_url: str = "postgresql+psycopg://talentscreen:talentscreen@localhost:5434/talentscreen"
    jwt_secret: str = Field(default="development-only-change-me", repr=False)
    llm_api_key: str | None = Field(default=None, repr=False)
    embedding_api_key: str | None = Field(default=None, repr=False)
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    demo_mode: bool = False

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
