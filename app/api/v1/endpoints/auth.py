from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.token import Token
from app.services.auth_service import authenticate_user, create_user
from app.core.security import create_access_token
from app.schemas.user import UserCreate, UserAuth

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=Token)
async def login(form_data: UserAuth = Depends()):
    """
    Логин пользователя.
    Принимает email и password (form-data), возвращает JWT токен.
    """
    # Проверяем пользователя
    user = authenticate_user(form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаём токен
    access_token = create_access_token(data={"sub": user.email})
    
    return Token(access_token=access_token, token_type="bearer")

@router.post("/registration")
async def registration(data: UserCreate, db=Depends(get_db)):
    create_user(db, UserCreate)

    