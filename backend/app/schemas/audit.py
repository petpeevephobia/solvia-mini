import uuid
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class AuditCreate(BaseModel):
    url: str = Field(..., max_length=2048)
    email: EmailStr

    @field_validator("url")
    @classmethod
    def url_must_be_http(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class AuditAccepted(BaseModel):
    audit_id: uuid.UUID
    status: Literal["queued"] = "queued"


class AuditStatusResponse(BaseModel):
    audit_id: uuid.UUID
    status: str
    error_message: str | None = None
