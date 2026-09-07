from fastapi import HTTPException, status
from sqlalchemy import select
from app.schemas.user import UserResponse, UserCreate
from app.infrastructure.db.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password, get_password_hash


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, email: str, password: str):
    """Аутентифицирует пользователя: проверяет, что такой есть и пароль верный"""

    user = await get_user_by_email(db, email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or not active",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(password, user.password_hash):
        return None
    return user


async def create_user(db: AsyncSession, user_model: UserCreate) -> User:
    exists = await get_user_by_email(db, user_model.email)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Имя пользователя уже занято",
        )

    user = User(
        name=user_model.name,
        password_hash=get_password_hash(user_model.password),
        username=await generate_username(user_model.email),
        email=user_model.email,
        phone=user_model.phone,
        birthday=user_model.birthday,
        timezone=user_model.timezone,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def generate_username(email: str) -> str:
    # Разделяем email на локальную часть и домен. Используем только первое вхождение
    username = email.split("@", maxsplit=1)
    # Так как при выполнении функции split() получаем list[], результат необходимо преобразовать в str
    username = str(username[0])
    # Приводим к нижнему регистру и убираем возможные лишние символы (например, точки)
    return username.lower().replace(".", "_").strip(" _")
