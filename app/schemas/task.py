# app/schemas/task.py
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

# ---------- Статусы и важность ----------
# ДОБАВЛЕНО: Literal-типы должны совпадать с CheckConstraint в models.py.
# При добавлении значения — правь ОБА в одном PR, иначе 500 на валидации.
TaskStatus = Literal["todo", "in_progress", "done", "cancelled"]
TaskImportance = Literal["low", "medium", "high", "critical"]

# Статусы, которые разрешено выставлять вручную через PATCH.
# 'done' пойдёт через отдельный эндпоинт /complete — там проставляется
# completed_at. Это защищает инвариант "status='done' ⇔ completed_at != NULL".
TaskManualStatus = Literal["todo", "in_progress", "cancelled"]


# ---------- Task schemas ----------

class TaskBase(BaseModel):
    """Общие поля для create/response. Без id/служебных дат."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    importance: TaskImportance = "medium"
    deadline: Optional[datetime] = None
    responsible_id: Optional[UUID] = None


class TaskCreate(TaskBase):
    """
    board_id берётся из URL (/boards/{board_id}/tasks), creator_id — из JWT.
    Пустое тело — нормально, но title обязателен.
    """
    pass


class TaskUpdate(BaseModel):
    """
    PATCH: все поля опциональны.
    В сервисе использовать payload.model_dump(exclude_unset=True),
    НЕ exclude_none=True — иначе нельзя будет стереть description,
    снять responsible_id или убрать deadline (передав null).
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    importance: Optional[TaskImportance] = None
    deadline: Optional[datetime] = None
    responsible_id: Optional[UUID] = None
    # ДОБАВЛЕНО: статус тоже меняется через PATCH, но без 'done'.
    # Завершение — отдельным эндпоинтом (см. TaskComplete).
    status: Optional[TaskManualStatus] = None


class TaskStatusUpdate(BaseModel):
    """
    Отдельная схема для PATCH /tasks/{id}/status — переключение колонки
    на канбане. Без 'done': для завершения используем TaskComplete.
    """
    status: TaskManualStatus


class TaskComplete(BaseModel):
    """
    POST /tasks/{id}/complete — завершение задачи.
    Сервис выставляет status='done' И completed_at=now() атомарно,
    чтобы инвариант не разъехался.
    """
    # ДОБАВЛЕНО: можно передать комментарий к завершению — попадёт в activity_log
    comment: Optional[str] = None


class TaskReopen(BaseModel):
    """
    POST /tasks/{id}/reopen — возврат из done/cancelled в работу.
    Симметрично TaskComplete: чистит completed_at и ставит status='todo'.
    """
    status: Literal["todo", "in_progress"] = "todo"


class TaskResponse(TaskBase):
    """Полное представление задачи (для списка и деталей)."""
    id: UUID
    board_id: UUID
    creator_id: UUID
    status: TaskStatus
    # ДОБАВЛЕНО: completed_at — клиенту важно видеть, когда задача закрыта
    completed_at: Optional[datetime] = None
    created_at: datetime
    # ДОБАВЛЕНО: updated_at — "обновлено N минут назад"
    updated_at: datetime
    # ИСПРАВЛЕНО: deleted_at НЕ отдаём — soft-deleted задачи фильтруются
    # в репозитории (WHERE deleted_at IS NULL)

    model_config = ConfigDict(from_attributes=True)


class TaskDetailResponse(TaskResponse):
    """
    ДОБАВЛЕНО: детальное представление для GET /tasks/{id}.
    Догружает автора и исполнителя через .creator / .responsible
    (требует selectinload в репозитории).
    """
    creator: "UserShort"
    responsible: Optional["UserShort"] = None


# ---------- Список с пагинацией ----------

class TaskListResponse(BaseModel):
    """
    ДОБАВЛЕНО: обёртка для списков с пагинацией.
    Курсорная пагинация (limit/offset) предпочтительнее страничной,
    потому что канбан грузит задачи "до N штук" без тотала.
    """
    items: list[TaskResponse]
    total: Optional[int] = None
    limit: int
    offset: int


# ---------- Валидация на уровне схемы ----------

@model_validator(mode="after")
def _check_deadline_in_future_or_past(self):
    """
    Мягкая проверка: deadline можно ставить и в прошлое (задача "сгорела"),
    но при создании это обычно ошибка. Оставляем на усмотрение сервиса —
    здесь только если нужно быстро отсеять очевидный мусор.
    """
    return self


# ---- Forward-refs ----
# ИСПРАВЛЕНО: импорт в конце — чтобы не получить циклическую зависимость
# (user.py может импортировать task.py в UserShort или UserDetail).
from app.schemas.user import UserShort  # noqa: E402

TaskDetailResponse.model_rebuild()