# app/api/v1/endpoints/tasks.py
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user  # поправь под свой проект
from app.core.dependencies import get_db                   # поправь под свой проект
from app.infrastructure.db.models import User
from app.schemas.task import (
    TaskComplete,
    TaskCreate,
    TaskDetailResponse,
    TaskListResponse,
    TaskReopen,
    TaskResponse,
    TaskStatus,
    TaskImportance,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.services.task_service import (
    TaskForbidden,
    TaskNotFound,
    TaskService,
    TaskValidationError,
)

router = APIRouter(prefix="/boards/{board_id}/tasks", tags=["tasks"])


def _service(db: AsyncSession = Depends(get_db)) -> TaskService:
    return TaskService(db)


# Единый маппинг доменных исключений в HTTP — здесь, не в сервисе.
def _handle(exc: Exception) -> HTTPException:
    if isinstance(exc, TaskNotFound):
        return HTTPException(status.HTTP_404_NOT_FOUND, str(exc))
    if isinstance(exc, TaskForbidden):
        return HTTPException(status.HTTP_403_FORBIDDEN, str(exc))
    if isinstance(exc, TaskValidationError):
        return HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc))
    return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal error")


# ---------- POST /boards/{board_id}/tasks ----------
@router.post(
    "",
    response_model=TaskDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать задачу",
)
async def create_task(
    board_id: UUID,
    payload: TaskCreate,
    current_user: User = Depends(get_current_user),
    svc: TaskService = Depends(_service),
):
    try:
        task = await svc.create(board_id, payload, current_user)
        # после commit'а подгружаем detail с creator/responsible
        return await svc.get(task.id, current_user)
    except (TaskNotFound, TaskForbidden, TaskValidationError) as e:
        raise _handle(e)


# ---------- GET /boards/{board_id}/tasks ----------
@router.get(
    "",
    response_model=TaskListResponse,
    summary="Список задач доски с фильтрами",
)
async def list_tasks(
    board_id: UUID,
    current_user: User = Depends(get_current_user),
    svc: TaskService = Depends(_service),
    status_filter: TaskStatus | None = Query(None, alias="status"),
    importance: TaskImportance | None = Query(None),
    responsible_id: UUID | None = Query(None),
    search: str | None = Query(None, min_length=2, max_length=100),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    try:
        items, total = await svc.list(
            board_id,
            current_user,
            status=status_filter,
            importance=importance,
            responsible_id=responsible_id,
            search=search,
            limit=limit,
            offset=offset,
        )
        return TaskListResponse(
            items=[TaskResponse.model_validate(t) for t in items],
            total=total,
            limit=limit,
            offset=offset,
        )
    except (TaskNotFound, TaskForbidden, TaskValidationError) as e:
        raise _handle(e)


# ---------- GET /boards/{board_id}/tasks/{task_id} ----------
@router.get(
    "/{task_id}",
    response_model=TaskDetailResponse,
    summary="Детали задачи",
)
async def get_task(
    board_id: UUID,  # в path для консистентности URL, но в выборке не нужен
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    svc: TaskService = Depends(_service),
):
    try:
        return await svc.get(task_id, current_user)
    except (TaskNotFound, TaskForbidden, TaskValidationError) as e:
        raise _handle(e)


# ---------- PATCH /boards/{board_id}/tasks/{task_id} ----------
@router.patch(
    "/{task_id}",
    response_model=TaskDetailResponse,
    summary="Частичное обновление задачи",
)
async def update_task(
    board_id: UUID,
    task_id: UUID,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_user),
    svc: TaskService = Depends(_service),
):
    try:
        await svc.update(task_id, payload, current_user)
        return await svc.get(task_id, current_user)
    except (TaskNotFound, TaskForbidden, TaskValidationError) as e:
        raise _handle(e)


# ---------- PATCH /boards/{board_id}/tasks/{task_id}/status ----------
@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
    summary="Сменить статус (канбан)",
)
async def change_status(
    board_id: UUID,
    task_id: UUID,
    payload: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    svc: TaskService = Depends(_service),
):
    try:
        return await svc.change_status(task_id, payload, current_user)
    except (TaskNotFound, TaskForbidden, TaskValidationError) as e:
        raise _handle(e)


# ---------- POST /boards/{board_id}/tasks/{task_id}/complete ----------
@router.post(
    "/{task_id}/complete",
    response_model=TaskResponse,
    summary="Завершить задачу (status=done, completed_at=now)",
)
async def complete_task(
    board_id: UUID,
    task_id: UUID,
    payload: TaskComplete,
    current_user: User = Depends(get_current_user),
    svc: TaskService = Depends(_service),
):
    try:
        return await svc.complete(task_id, payload, current_user)
    except (TaskNotFound, TaskForbidden, TaskValidationError) as e:
        raise _handle(e)


# ---------- POST /boards/{board_id}/tasks/{task_id}/reopen ----------
@router.post(
    "/{task_id}/reopen",
    response_model=TaskResponse,
    summary="Вернуть задачу в работу (completed_at=null)",
)
async def reopen_task(
    board_id: UUID,
    task_id: UUID,
    payload: TaskReopen,
    current_user: User = Depends(get_current_user),
    svc: TaskService = Depends(_service),
):
    try:
        return await svc.reopen(task_id, payload, current_user)
    except (TaskNotFound, TaskForbidden, TaskValidationError) as e:
        raise _handle(e)


# ---------- DELETE /boards/{board_id}/tasks/{task_id} ----------
@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete задачи (owner/admin)",
)
async def delete_task(
    board_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    svc: TaskService = Depends(_service),
):
    try:
        await svc.soft_delete(task_id, current_user)
    except (TaskNotFound, TaskForbidden, TaskValidationError) as e:
        raise _handle(e)