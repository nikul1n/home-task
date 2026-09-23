# app/repositories/task_repo.py
from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.db.models import Task


class TaskRepo:
    """
    Только SQL. Никаких проверок прав и бизнес-правил —
    это задача сервиса. Репозиторий всегда фильтрует deleted_at IS NULL,
    кроме явного include_deleted.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self, task_id: UUID, *, include_deleted: bool = False
    ) -> Optional[Task]:
        stmt = select(Task).where(Task.id == task_id)
        if not include_deleted:
            stmt = stmt.where(Task.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_detail(self, task_id: UUID) -> Optional[Task]:
        """С creator/responsible, чтобы отдать TaskDetailResponse без N+1."""
        stmt = (
            select(Task)
            .where(Task.id == task_id, Task.deleted_at.is_(None))
            .options(
                selectinload(Task.creator),
                selectinload(Task.responsible),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_board(
        self,
        board_id: UUID,
        *,
        status: Optional[str] = None,
        importance: Optional[str] = None,
        responsible_id: Optional[UUID] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[Task], int]:
        # Базовый фильтр: активные задачи доски
        conditions = [Task.board_id == board_id, Task.deleted_at.is_(None)]
        if status:
            conditions.append(Task.status == status)
        if importance:
            conditions.append(Task.importance == importance)
        if responsible_id:
            conditions.append(Task.responsible_id == responsible_id)
        if search:
            # Использует idx_tasks_search (GIN FTS)
            conditions.append(
                func.to_tsvector("russian", Task.title).op("@@")(
                    func.plainto_tsquery("russian", search)
                )
            )

        count_stmt = select(func.count()).select_from(Task).where(*conditions)
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = (
            select(Task)
            .where(*conditions)
            .order_by(Task.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        items = (await self.db.execute(stmt)).scalars().all()
        return items, total

    async def add(self, task: Task) -> Task:
        self.db.add(task)
        await self.db.flush()
        return task

    async def soft_delete(self, task: Task) -> None:
        from datetime import datetime, timezone
        task.deleted_at = datetime.now(tz=timezone.utc)
        await self.db.flush()