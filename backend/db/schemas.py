from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Optional
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class AuthProviderEnum(str, Enum):
    EMAIL = "email"
    GOOGLE = "google"


class ResearchStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class MessageRoleEnum(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    """Base user fields"""
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: Optional[str] = None
    provider: AuthProviderEnum = AuthProviderEnum.EMAIL
    provider_id: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response - public profile"""
    id: UUID
    provider: AuthProviderEnum
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserWithSessions(UserResponse):
    """Schema for user with their research sessions"""
    research_sessions: list["ResearchSessionResponse"] = []

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Chat Message Schemas
# ============================================================================

class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message"""
    role: MessageRoleEnum
    content: str


class ChatMessageResponse(BaseModel):
    """Schema for chat message response"""
    id: UUID
    session_id: UUID
    role: MessageRoleEnum
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Agent Event Schemas
# ============================================================================

class AgentEventResponse(BaseModel):
    """Schema for agent event response"""
    id: UUID
    session_id: UUID
    agent_name: str
    event_type: str
    payload: Optional[dict] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Research Session Schemas
# ============================================================================

class ResearchSessionCreate(BaseModel):
    """Schema for creating a new research session"""
    topic: str


class ResearchSessionUpdate(BaseModel):
    """Schema for updating a research session"""
    topic: Optional[str] = None
    status: Optional[ResearchStatusEnum] = None
    report_json: Optional[dict] = None
    error_message: Optional[str] = None


class ResearchSessionResponse(BaseModel):
    """Schema for research session response"""
    id: UUID
    user_id: UUID
    topic: str
    status: ResearchStatusEnum
    report_json: Optional[dict] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResearchSessionDetail(ResearchSessionResponse):
    """Schema for detailed research session with chat history and events"""
    chat_messages: list[ChatMessageResponse] = []
    agent_events: list[AgentEventResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Pagination Schemas
# ============================================================================

class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper"""
    items: list
    total: int
    skip: int
    limit: int
