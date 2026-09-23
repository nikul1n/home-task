# app/schemas/board.py
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ---------- Роли ----------
# ДОБАВЛЕНО: два разных Literal, потому что набор ролей для создания/смены
# и для чтения отличается. При создании/смене 'owner' запрещён —
# владелец доски определяется через Board.creator_id и создаётся один раз
# вместе с доской (см. board_service.create_board).
BoardUserRole = Literal["owner", "admin", "member", "viewer"]
BoardUserMutableRole = Literal["admin", "member", "viewer"]


# ---------- Board schemas ----------


class BoardBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class BoardCreate(BoardBase):
    pass  # creator_id будет добавлен из токена в эндпоинте


class BoardUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class BoardResponse(BoardBase):
    id: UUID
    creator_id: UUID
    created_at: datetime
    updated_at: datetime
    # deleted_at: Optional[datetime] = None  # можно не включать, если не нужно

    model_config = ConfigDict(from_attributes=True)


# ---------- Board member schemas ----------

# BoardUserRole = Literal["owner", "admin", "member", "viewer"]


class BoardUserBase(BaseModel):
    pass
    # role: BoardUserRole = "member"


class BoardUserCreate(BoardUserBase):
    # ИСПРАВЛЕНО: запрет на role="owner" при создании участника.
    # Владелец один — создаётся автоматически при создании доски.
    # Попытка добавить второго owner = нарушение инварианта.
    role: BoardUserMutableRole = "member"
    user_id: UUID


class BoardUserRead(BoardUserBase):
    role: BoardUserRole
    id: UUID
    board_id: UUID
    user_id: UUID
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)

    # TODO: Плюс эндпоинт PATCH /boards/{id}/members/{user_id}.


class BoardUserUpdate(BaseModel):
    """ДОБАВЛЕНО: схема для смены роли участника (PATCH .../members/{user_id})."""

    role: BoardUserMutableRole


class BoardMemberRead(BoardUserRead):
    """
    ДОБАВЛЕНО: расширенное представление участника с краткой инфой о юзере.
    Нужно, чтобы фронт не делал N+1 запросов за username/avatar_url.
    Требует join или selectinload в репозитории.
    """

    # user подгружается через .user relationship в модели BoardUser.
    # Схема UserShort должна быть определена в schemas/user.py:
    #   class UserShort(BaseModel):
    #       id: UUID
    #       username: str
    #       name: str
    #       avatar_url: Optional[str] = None
    #       model_config = ConfigDict(from_attributes=True)
    user: "UserShort"


class BoardDetailResponse(BoardResponse):
    """
    ДОБАВЛЕНО: детальное представление доски для GET /boards/{id}.
    Включает участников — экономит клиенту один round-trip.
    Для списка досок (GET /boards) используем обычный BoardResponse
    без участников — иначе разрастётся payload.
    """

    members: list[BoardMemberRead] = []

    # ---- Forward-refs ----


# ИСПРАВЛЕНО: ниже — резолв forward reference 'UserShort' из schemas/user.py.
# ВАЖНО: импорт в конце файла, чтобы не получить цикл (user.py может
# импортировать board.py).
from app.schemas.user import UserShort  # noqa: E402

BoardMemberRead.model_rebuild()
