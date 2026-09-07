# app/schemas/board.py
from datetime import datetime
from uuid import UUID
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field

# ---------- Board schemas ----------

class BoardBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class BoardCreate(BoardBase):
    pass  # creator_id будет добавлен из токена в эндпоинте

class BoardUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None

class BoardRead(BoardBase):
    id: UUID
    creator_id: UUID
    created_at: datetime
    deleted_at: Optional[datetime] = None  # можно не включать, если не нужно

    model_config = ConfigDict(from_attributes=True)

# ---------- Board member schemas ----------

BoardUserRole = Literal["owner", "admin", "member", "viewer"]

class BoardUserBase(BaseModel):
    role: BoardUserRole = "member"

class BoardUserCreate(BoardUserBase):
    user_id: UUID

class BoardUserRead(BoardUserBase):
    id: UUID
    board_id: UUID
    user_id: UUID
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)