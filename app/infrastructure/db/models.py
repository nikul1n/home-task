import uuid
from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # ИЗМЕНЕНО: для username и email снят unique=True — уникальность теперь через partial index
    # (нужно для поддержки soft delete + повторной регистрации на тот же email)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)

    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        # Проверка: только цифры (если телефон указан)
        CheckConstraint("phone ~ '^[0-9]+$'", name="ck_users_phone_digits"),
        nullable=True,
    )

    birthday: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="Europe/Moscow"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ДОБАВЛЕНО: partial unique indexes (Postgres):
    # уникальность email/username только среди активных (не удалённых) записей.
    # Позволяет: soft-delete юзера → регистрация нового с тем же email.
    __table_args__ = (
        Index(
            "uq_users_email_active",
            "email",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "uq_users_username_active",
            "username",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    # Связи
    boards_created: Mapped[list["Board"]] = relationship(
        back_populates="creator", foreign_keys="Board.creator_id"
    )
    tasks_created: Mapped[list["Task"]] = relationship(
        back_populates="creator", foreign_keys="Task.creator_id"
    )
    tasks_assigned: Mapped[list["Task"]] = relationship(
        back_populates="responsible", foreign_keys="Task.responsible_id"
    )
    board_memberships: Mapped[list["BoardUser"]] = relationship(back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")


class Board(Base):
    __tablename__ = "boards"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # ДОБАВЛЕНО: updated_at, аналогично Task — пригодится для сортировки
    # "недавно обновлённые доски"
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Связи
    creator: Mapped["User"] = relationship(
        back_populates="boards_created", foreign_keys=[creator_id]
    )
    members: Mapped[list["BoardUser"]] = relationship(back_populates="board")
    tasks: Mapped[list["Task"]] = relationship(back_populates="board")


class BoardUser(Base):
    __tablename__ = "board_users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    board_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "role IN ('owner', 'admin', 'member', 'viewer')", name="ck_board_users_role"
        ),
        nullable=False,
        server_default="member",
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        UniqueConstraint("board_id", "user_id", name="uq_board_user"),
        # ДОБАВЛЕНО: индекс на user_id (в uq_board_user он второй — для
        # запроса "все доски юзера" не годится)
        Index("idx_board_users_user", "user_id"),
    )

    # Связи
    board: Mapped["Board"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="board_memberships")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    board_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,  # ДОБАВЛЕНО: индекс на FK
        index=True,
    )
    responsible_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        CheckConstraint(
            "status IN ('todo', 'in_progress', 'done', 'cancelled')",
            name="ck_tasks_status",
        ),
        nullable=False,
        server_default="todo",
    )
    importance: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "importance IN ('low', 'medium', 'high', 'critical')",
            name="ck_tasks_importance",
        ),
        nullable=False,
        server_default="medium",
    )

    deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # ИСПРАВЛЕНО: добавлен onupdate=text("now()") — server_default срабатывает
    # только при INSERT, поэтому без onupdate поле оставалось прежним при UPDATE.
    # (Альтернатива для bulletproof-варианта — триггер в БД через миграцию.)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),  # ORM-уровень
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Индексы
    __table_args__ = (
        Index("idx_tasks_board_status", "board_id", "status"),
        Index("idx_tasks_responsible", "responsible_id"),
        Index("idx_tasks_deadline", "deadline"),
        Index("idx_tasks_created_at", "created_at"),
        # Индекс для полнотекстового поиска (PostgreSQL).
        # Для больших таблиц есть смысл перейти на GENERATED COLUMN STORED (PG12+),
        # сейчас — expression index (пересчитывается на каждый write).
        Index(
            "idx_tasks_search",
            text("to_tsvector('russian', title || ' ' || COALESCE(description, ''))"),
            postgresql_using="gin",
        ),
    )

    # Связи
    board: Mapped["Board"] = relationship(back_populates="tasks")
    creator: Mapped["User"] = relationship(
        back_populates="tasks_created", foreign_keys=[creator_id]
    )
    responsible: Mapped[Optional["User"]] = relationship(
        back_populates="tasks_assigned", foreign_keys=[responsible_id]
    )


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True
    )
    board_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("boards.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(255), nullable=False)

    # TODO: Предлагается: dict[str, Any] вместо dict — точнее для типизации JSONB
    old_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    new_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # ДОБАВЛЕНО: индексы под частые запросы к журналу.
    # activity_log растёт быстрее всех — индексы нужны до продакшена.
    __table_args__ = (
        Index("idx_activity_log_user_created", "user_id", "created_at"),
        Index("idx_activity_log_task", "task_id"),
        Index("idx_activity_log_board_created", "board_id", "created_at"),
    )

    # Связи (по желанию)
    user: Mapped["User"] = relationship()
    task: Mapped[Optional["Task"]] = relationship()
    board: Mapped[Optional["Board"]] = relationship()


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_read: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (Index("idx_notifications_user_read", "user_id", "is_read"),)

    # Связи
    user: Mapped["User"] = relationship(back_populates="notifications")
