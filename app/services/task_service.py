# app/services/task_service.py
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import ActivityLog, BoardUser, Task
from app.repositories.task_repo import TaskRepo
from app.schemas.task import (
    TaskComplete,
    TaskCreate,
    TaskReopen,
    TaskStatusUpdate,
    TaskUpdate,
)


# --- Доменные исключения ---
# Эндпоинт ловит их и маппит в HTTP-коды. Не поднимаем HTTPException
# внутри сервиса — сервис не знает про транспорт.
class TaskError(Exception):
    """База для всех доменных ошибок задачи."""


class TaskNotFound(TaskError):
    pass


class TaskForbidden(TaskError):
    pass


class TaskValidationError(TaskError):
    pass


# Роли, которым разрешено создавать/менять задачи.
_WRITE_ROLES = {"owner", "admin", "member"}


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TaskRepo(db)

    # ---------- Проверки доступа ----------

    async def _get_board_role(self, board_id: UUID, user_id: UUID) -> str:
        """Возвращает роль юзера на доске или бросает TaskForbidden."""
        stmt = select(BoardUser).where(
            BoardUser.board_id == board_id,
            BoardUser.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        membership = result.scalar_one_or_none()
        if membership is None:
            # Не палим существование доски — отдаём 403, не 404.
            raise TaskForbidden("You are not a member of this board")
        return membership.role

    async def _ensure_can_write(self, board_id: UUID, user_id: UUID) -> str:
        role = await self._get_board_role(board_id, user_id)
        if role not in _WRITE_ROLES:
            raise TaskForbidden(f"Role '{role}' cannot modify tasks")
        return role

    async def _ensure_member(self, board_id: UUID, user_id: UUID) -> None:
        """Проверка для responsible_id — исполнитель должен быть на доске."""
        await self._get_board_role(board_id, user_id)

    # ---------- Activity log ----------

    async def _log(
        self,
        *,
        user_id: UUID,
        action: str,
        task_id: UUID | None = None,
        board_id: UUID | None = None,
        old: dict | None = None,
        new: dict | None = None,
    ) -> None:
        self.db.add(
            ActivityLog(
                user_id=user_id,
                task_id=task_id,
                board_id=board_id,
                action=action,
                old_value=old,
                new_value=new,
            )
        )

    # ---------- Публичные методы ----------

    async def create(
        self, board_id: UUID, payload: TaskCreate, current_user
    ) -> Task:
        await self._ensure_can_write(board_id, current_user.id)

        # Инвариант: исполнитель должен быть участником доски.
        if payload.responsible_id is not None:
            await self._ensure_member(board_id, payload.responsible_id)

        task = Task(
            board_id=board_id,
            creator_id=current_user.id,
            **payload.model_dump(),
        )
        await self.repo.add(task)

        await self._log(
            user_id=current_user.id,
            task_id=task.id,
            board_id=board_id,
            action="task.created",
            new={"title": task.title, "responsible_id": str(task.responsible_id)
                 if task.responsible_id else None},
        )
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get(self, task_id: UUID, current_user) -> Task:
        task = await self.repo.get_detail(task_id)
        if task is None:
            raise TaskNotFound("Task not found")
        await self._get_board_role(task.board_id, current_user.id)  # доступ
        return task

    async def list(
        self,
        board_id: UUID,
        current_user,
        *,
        status: str | None = None,
        importance: str | None = None,
        responsible_id: UUID | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Task], int]:
        # Любой участник доски (включая viewer) может читать список.
        await self._get_board_role(board_id, current_user.id)
        items, total = await self.repo.list_by_board(
            board_id,
            status=status,
            importance=importance,
            responsible_id=responsible_id,
            search=search,
            limit=limit,
            offset=offset,
        )
        return list(items), total

    async def update(
        self, task_id: UUID, payload: TaskUpdate, current_user
    ) -> Task:
        task = await self.repo.get_by_id(task_id)
        if task is None:
            raise TaskNotFound("Task not found")
        await self._ensure_can_write(task.board_id, current_user.id)

        # exclude_unset — чтобы PATCH отличал "не передано" от "передано null"
        data = payload.model_dump(exclude_unset=True)

        # Проверка смены исполнителя
        if "responsible_id" in data and data["responsible_id"] is not None:
            await self._ensure_member(task.board_id, data["responsible_id"])

        # Не разрешаем ручную установку status='done' — только через complete()
        if data.get("status") == "done":
            raise TaskValidationError(
                "Use /tasks/{id}/complete to finish a task"
            )

        old_snapshot = self._snapshot(task)
        for field, value in data.items():
            setattr(task, field, value)

        await self._log(
            user_id=current_user.id,
            task_id=task.id,
            board_id=task.board_id,
            action="task.updated",
            old=old_snapshot,
            new=data,
        )
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def change_status(
        self, task_id: UUID, payload: TaskStatusUpdate, current_user
    ) -> Task:
        task = await self.repo.get_by_id(task_id)
        if task is None:
            raise TaskNotFound("Task not found")
        await self._ensure_can_write(task.board_id, current_user.id)

        # Переход в working-статусы: completed_at должен быть None.
        # Если задача была done и её вернули в in_progress — чистим.
        old_status = task.status
        task.status = payload.status
        if payload.status != "done":
            task.completed_at = None

        await self._log(
            user_id=current_user.id,
            task_id=task.id,
            board_id=task.board_id,
            action="task.status_changed",
            old={"status": old_status},
            new={"status": payload.status},
        )
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def complete(
        self, task_id: UUID, payload: TaskComplete, current_user
    ) -> Task:
        task = await self.repo.get_by_id(task_id)
        if task is None:
            raise TaskNotFound("Task not found")
        await self._ensure_can_write(task.board_id, current_user.id)

        if task.status == "done":
            return task  # идемпотентно

        old_status = task.status
        task.status = "done"
        task.completed_at = datetime.now(tz=timezone.utc)

        await self._log(
            user_id=current_user.id,
            task_id=task.id,
            board_id=task.board_id,
            action="task.completed",
            old={"status": old_status},
            new={"status": "done", "comment": payload.comment},
        )
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def reopen(
        self, task_id: UUID, payload: TaskReopen, current_user
    ) -> Task:
        task = await self.repo.get_by_id(task_id)
        if task is None:
            raise TaskNotFound("Task not found")
        await self._ensure_can_write(task.board_id, current_user.id)

        if task.status not in ("done", "cancelled"):
            raise TaskValidationError("Only done/cancelled tasks can be reopened")

        task.status = payload.status
        task.completed_at = None

        await self._log(
            user_id=current_user.id,
            task_id=task.id,
            board_id=task.board_id,
            action="task.reopened",
            new={"status": payload.status},
        )
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def soft_delete(self, task_id: UUID, current_user) -> None:
        task = await self.repo.get_by_id(task_id)
        if task is None:
            raise TaskNotFound("Task not found")

        # Удалять может только owner/admin — member нет.
        role = await self._get_board_role(task.board_id, current_user.id)
        if role not in {"owner", "admin"}:
            raise TaskForbidden("Only owner/admin can delete tasks")

        await self.repo.soft_delete(task)
        await self._log(
            user_id=current_user.id,
            task_id=task.id,
            board_id=task.board_id,
            action="task.deleted",
        )
        await self.db.commit()

    # ---------- helpers ----------

    @staticmethod
    def _snapshot(task: Task) -> dict:
        """Снимок редактируемых полей для activity_log.old_value."""
        return {
            "title": task.title,
            "description": task.description,
            "importance": task.importance,
            "deadline": task.deadline.isoformat() if task.deadline else None,
            "responsible_id": str(task.responsible_id)
            if task.responsible_id else None,
            "status": task.status,
        }