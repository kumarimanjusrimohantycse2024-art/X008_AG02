from uuid import UUID

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models import JobStatus, RequirementPriority


class JobCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    department: str | None = None
    description: str = Field(min_length=1)

    @field_validator("title", "description")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class JobUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    department: str | None = None
    description: str | None = Field(default=None, min_length=1)
    status: JobStatus | None = None

    @field_validator("title", "description")
    @classmethod
    def reject_blank_update(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("must not be blank")
        return value.strip() if value is not None else None


class RequirementDraft(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    priority: RequirementPriority
    minimum_years: Decimal | None = Field(default=None, ge=0)
    weight: Decimal = Field(gt=0)
    aliases: list[str] = Field(default_factory=list)
    evidence_expectations: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name", "description")
    @classmethod
    def reject_blank_requirement_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("aliases")
    @classmethod
    def validate_aliases(cls, values: list[str]) -> list[str]:
        cleaned = [value.strip() for value in values]
        if any(not value for value in cleaned):
            raise ValueError("aliases must not be blank")
        return list(dict.fromkeys(cleaned))


class RequirementReviewRequest(BaseModel):
    requirements: list[RequirementDraft]

    @model_validator(mode="after")
    def reject_duplicate_names(self) -> "RequirementReviewRequest":
        normalized = [item.name.casefold().strip() for item in self.requirements]
        if len(normalized) != len(set(normalized)):
            raise ValueError("duplicate requirement names are not allowed")
        return self


class RequirementResponse(RequirementDraft):
    model_config = ConfigDict(from_attributes=True)
    id: UUID | None = None


class RequirementAnalysisResponse(BaseModel):
    requirements: list[RequirementDraft]
    source: str


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    department: str | None
    description: str
    status: JobStatus
    created_by: UUID
    created_at: datetime
    required_count: int = 0
    preferred_count: int = 0
