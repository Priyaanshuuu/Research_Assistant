from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

class StartResearchRequest(BaseModel):
    topic: str = Field(
        min_length=10,
        max_length=500,
        description="The research topic — must be a meaningful question or subject",
    )


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