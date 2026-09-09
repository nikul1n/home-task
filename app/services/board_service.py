# from sqlalchemy.ext.asyncio import AsyncSession
# from app.infrastructure.db.models import Board
# from app.schemas.board import BoardCreate, BoardResponse
# from fastapi import HTTPException, status
# from uuid import UUID

# async def get_board_by_id(db: AsyncSession, id: UUID):
#     result = await db.execute(select(Board).where(Board.id == UUID))
#     return result.scalar_one_or_none()

# async def create_board(db: AsyncSession, board_model: BoardResponse) -> Board:
    
    
#     exists = await get_board_by_id(db, board_model.id)
#     if exists:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Доска не найдена",
#         )

#     board = BoardResponse(
#     title=board_model.title
#     description=board_model.
#     creator_id=user
#     created_at= 
#     )

#     db.add(user)
#     await db.commit()
#     await db.refresh(user)
#     return user

from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.board_repo import BoardRepository
from app.schemas.board import BoardCreate, BoardUpdate
from app.infrastructure.db.models import Board

class BoardService:
    def __init__(self, db: AsyncSession):
        self.repo = BoardRepository(db)

    async def create_board(self, data: BoardCreate, creator_id: UUID) -> Board:
        return await self.repo.create(data, creator_id)

    async def get_board(self, board_id: UUID, user_id: UUID) -> Board:
        board = await self.repo.get_by_id(board_id, user_id)
        if not board:
            raise HTTPException(status_code=404, detail="Доска не найдена или у вас нет доступа")
        return board

    async def list_boards(self, user_id: UUID) -> list[Board]:
        return await self.repo.list_for_user(user_id)

    async def update_board(self, board_id: UUID, user_id: UUID, data: BoardUpdate) -> Board:
        # Проверяем права (только owner или admin)
        role = await self.repo.check_user_role(board_id, user_id)
        if role not in ("owner", "admin"):
            raise HTTPException(status_code=403, detail="Недостаточно прав для изменения доски")
        board = await self.repo.update(board_id, data)
        if not board:
            raise HTTPException(status_code=404, detail="Доска не найдена")
        return board

    async def delete_board(self, board_id: UUID, user_id: UUID) -> None:
        role = await self.repo.check_user_role(board_id, user_id)
        if role != "owner":
            raise HTTPException(status_code=403, detail="Только владелец может удалить доску")
        success = await self.repo.soft_delete(board_id)
        if not success:
            raise HTTPException(status_code=404, detail="Доска не найдена")

    async def add_member(self, board_id: UUID, current_user_id: UUID, new_user_id: UUID, role: str):
        # Проверяем права (owner или admin)
        current_role = await self.repo.check_user_role(board_id, current_user_id)
        if current_role not in ("owner", "admin"):
            raise HTTPException(status_code=403, detail="Недостаточно прав для добавления участников")
        member = await self.repo.add_member(board_id, new_user_id, role)
        return member