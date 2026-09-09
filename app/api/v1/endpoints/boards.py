# # Управление доскам
# # create post
# # read get
# # update put
# # delite delite

# from app.schemas.board import BoardResponse, BoardCreate, BoardUpdate
# from fastapi import APIRouter, Depends, HTTPException, status
# from app.infrastructure.db.session import get_db

# router = APIRouter(prefix="/boards", tags=["boards"])

# @router.post("/create_board", response_model=BoardResponse)
# async def create_board(form_data: BoardCreate, db=Depends(get_db)):
#     board = await 



# user = await authenticate_user(db, form_data.email, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     # Создаём токен
#     access_token = create_access_token(data={"sub": user.email})

#     return Token(access_token=access_token, token_type="bearer")

from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.session import get_db
from app.api.v1.dependencies import get_current_user
from app.schemas.board import BoardCreate, BoardUpdate, BoardResponse, BoardUserCreate, BoardUserRead
from app.services.board_service import BoardService
from app.infrastructure.db.models import User

router = APIRouter()

@router.post("/create_board", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
async def create_board(
    data: BoardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = BoardService(db)
    return await service.create_board(data, current_user.id)

@router.get("/{board_id}", response_model=BoardResponse)
async def get_board(
    board_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = BoardService(db)
    return await service.get_board(board_id, current_user.id)

@router.get("/", response_model=list[BoardResponse])
async def list_boards(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = BoardService(db)
    return await service.list_boards(current_user.id)

@router.patch("/{board_id}", response_model=BoardResponse)
async def update_board(
    board_id: UUID,
    data: BoardUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = BoardService(db)
    return await service.update_board(board_id, current_user.id, data)

@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = BoardService(db)
    await service.delete_board(board_id, current_user.id)

@router.post("/{board_id}/members", response_model=BoardUserRead, status_code=status.HTTP_201_CREATED)
async def add_member(
    board_id: UUID,
    data: BoardUserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = BoardService(db)
    return await service.add_member(board_id, current_user.id, data.user_id, data.role)