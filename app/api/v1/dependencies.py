from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token
from app.infrastructure.db.models import User
from app.infrastructure.db.session import get_db
# from app.schemas.user import UserResponse
from app.services.auth_service import get_user_by_email

# OAuth2PasswordBearer — встроенная зависимость FastAPI
# Она извлекает токен из заголовка Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(db = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
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
    email = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    # Проверяем, что пользователь существует
    user = await get_user_by_email(db, email)
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


# app/api/deps.py
# from uuid import UUID
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from sqlalchemy.ext.asyncio import AsyncSession
# from jose import JWTError, jwt
# from app.core.config import settings
# from app.db.session import get_async_db
# from app.models.user import User

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# async def get_current_user(
#     token: str = Depends(oauth2_scheme),
#     db: AsyncSession = Depends(get_async_db)
# ) -> User:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Не удалось проверить учётные данные",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
#         user_id: str = payload.get("sub")
#         if user_id is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception

#     user = await db.get(User, UUID(user_id))
#     if user is None or not user.is_active:
#         raise credentials_exception
#     return user