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
    if not user:
        return None
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
        password_hash=get_password_hash(user_model.password),
        email=user_model.email,
        phone=user_model.phone,
        birthday=user_model.birthday,
        timezone=user_model.timezone,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
