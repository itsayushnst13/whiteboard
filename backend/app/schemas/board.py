from datetime import datetime

from pydantic import BaseModel, Field


class BoardCreateRequest(BaseModel):
    name: str = Field(default="Untitled board", min_length=1, max_length=200)


class BoardUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class BoardResponse(BaseModel):
    id: int
    room_id: str
    name: str
    created_at: datetime
    updated_at: datetime
