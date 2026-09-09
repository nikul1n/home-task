from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models import Board, BoardUser
from app.schemas.board import BoardCreate, BoardUpdate

class BoardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: BoardCreate, creator_id: UUID) -> Board:
        board = Board(
            title=data.title,
            description=data.description,
            creator_id=creator_id
        )
        self.db.add(board)
        await self.db.flush()  # получаем board.id

        # Добавляем создателя как владельца
        member = BoardUser(
            board_id=board.id,
            user_id=creator_id,
            role="owner"
        )
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(board)
        return board

    async def get_by_id(self, board_id: UUID, user_id: UUID) -> Board | None:
        # Возвращаем доску только если пользователь участник
        stmt = (
            select(Board)
            .join(BoardUser, BoardUser.board_id == Board.id)
            .where(Board.id == board_id, BoardUser.user_id == user_id, Board.deleted_at.is_(None))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: UUID) -> list[Board]:
        stmt = (
            select(Board)
            .join(BoardUser, BoardUser.board_id == Board.id)
            .where(BoardUser.user_id == user_id, Board.deleted_at.is_(None))
            .order_by(Board.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, board_id: UUID, data: BoardUpdate) -> Board | None:
        board = await self.db.get(Board, board_id)
        if not board or board.deleted_at is not None:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(board, key, value)
        await self.db.commit()
        await self.db.refresh(board)
        return board

    async def soft_delete(self, board_id: UUID) -> bool:
        board = await self.db.get(Board, board_id)
        if not board or board.deleted_at is not None:
            return False
        board.deleted_at = datetime.utcnow()
        await self.db.commit()
        return True

    async def check_user_role(self, board_id: UUID, user_id: UUID) -> str | None:
        stmt = select(BoardUser.role).where(
            BoardUser.board_id == board_id,
            BoardUser.user_id == user_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def add_member(self, board_id: UUID, user_id: UUID, role: str = "member") -> BoardUser:
        member = BoardUser(board_id=board_id, user_id=user_id, role=role)
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)
        return member