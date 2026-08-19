from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.token import Token
from app.services.user_service import authenticate_user, get_user_by_useremail
from app.core.security import create_access_token
from app.schemas.user import UserCreate

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Логин пользователя.
    Принимает username и password (form-data), возвращает JWT токен.
    """
    # Проверяем пользователя
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаём токен
    access_token = create_access_token(data={"sub": user.username})
    
    return Token(access_token=access_token, token_type="bearer")

@router.post("/registration")
async def registration(data: UserCreate = Depends()):
    user = get_user_by_useremail(data.email)
    if not user:
        # TODO: Создать объект в базе данных SQLalchemy и настроить сам SQLalchemy
        # В DEpends надо сделать специальную функцию которая будет подключаться к БД 

        # new_user Создать объект в базе данных SQLalchemy
            email = data.email
        
    else: raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="This email is already in use",
    )