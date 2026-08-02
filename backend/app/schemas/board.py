from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

BoardRole = Literal["owner", "editor", "viewer"]
CollaboratorRole = Literal["editor", "viewer"]


class BoardCreateRequest(BaseModel):
    name: str = Field(default="Untitled board", min_length=1, max_length=200)


class BoardUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class BoardResponse(BaseModel):
    id: int
    room_id: str
    name: str
    owner_id: int
    role: BoardRole
    created_at: datetime
    updated_at: datetime


class ShareBoardRequest(BaseModel):
    """Invite a collaborator by email. Idempotent — inviting someone who
    is already a collaborator just updates their role."""

    email: EmailStr
    role: CollaboratorRole = "editor"


class CollaboratorResponse(BaseModel):
    user_id: int
    email: str
    display_name: str
    role: CollaboratorRole
    created_at: datetime
