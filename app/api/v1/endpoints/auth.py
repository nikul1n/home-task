from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
from app.infrastructure.db.session import get_db
from app.schemas.token import Token
from app.services.auth_service import authenticate_user, create_user
from app.core.security import create_access_token
from app.schemas.user import UserCreate, UserAuth, UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(form_data: UserAuth, db=Depends(get_db)):
    """
    Логин пользователя.
    Принимает email и password (form-data), возвращает JWT токен.
    """
    # Проверяем пользователя
    user = await authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Создаём токен
    access_token = create_access_token(data={"sub": user.email})

    return Token(access_token=access_token, token_type="bearer")


@router.post("/registration", response_model=UserResponse)
async def registration(data: UserCreate, db=Depends(get_db)):
    user = await create_user(db, data)
    return user
