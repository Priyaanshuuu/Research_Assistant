from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str | None = Field(default=None, max_length=100)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if v.isdigit():
            raise ValueError("Password must not be all digits")
        if v.isalpha():
            raise ValueError("Password must contain at least one number or symbol")
        return v

    @field_validator("name")
    @classmethod
    def name_no_html(cls, v: str | None) -> str | None:
        if v and ("<" in v or ">" in v):
            raise ValueError("Name must not contain HTML")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class StartResearchRequest(BaseModel):
    topic: str = Field(
        min_length=10,
        max_length=500,
        description="Research topic — must be a meaningful question or subject",
    )

    @field_validator("topic")
    @classmethod
    def topic_not_blank(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 10:
            raise ValueError("Topic must be at least 10 non-whitespace characters")
        if stripped.isdigit():
            raise ValueError("Topic must be a meaningful research question")
        return stripped


class AgentEventOut(BaseModel):
    id: UUID
    session_id: UUID
    agent_name: str
    event_type: str
    payload: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ResearchSessionOut(BaseModel):
    id: UUID
    user_id: UUID
    topic: str
    status: str
    report_json: dict[str, Any] | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    agent_events: list[AgentEventOut] = []

    model_config = {"from_attributes": True}


class StartResearchResponse(BaseModel):
    session_id: UUID
    status: str
    message: str


class ResearchStatusResponse(BaseModel):
    session_id: UUID
    status: str
    progress_pct: int = Field(ge=0, le=100)
    latest_event: str | None
    error_message: str | None


class ChatRequest(BaseModel):
    session_id: UUID
    message: str = Field(min_length=1, max_length=2000)

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message must not be blank")
        return v.strip()


class ChatMessageOut(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    user_message: ChatMessageOut
    assistant_message: ChatMessageOut

class ExportRequest(BaseModel):
    session_id: UUID
    format: str = Field(default="pdf", pattern="^(pdf|markdown)$")