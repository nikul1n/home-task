from fastapi import APIRouter, Depends
from app.schemas.user import UserResponse
from app.api.v1.dependencies import get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_active_user)):
    """
    Возвращает информацию о текущем пользователе.
    Требует валидный JWT токен в заголовке Authorization.
    """
    return current_user
