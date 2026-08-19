from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token
from app.services.user_service import get_user_by_username
from app.schemas.token import TokenData
from app.schemas.user import User

# OAuth2PasswordBearer — встроенная зависимость FastAPI
# Она извлекает токен из заголовка Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Извлекает текущего пользователя из JWT токена.
    Это сердце нашей авторизации!
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Декодируем токен
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # Извлекаем имя пользователя
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # Проверяем, что пользователь существует
    user = get_user_by_username(username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Проверяет, что пользователь не заблокирован"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user
