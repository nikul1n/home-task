from app.schemas.user import UserResponse, UserCreate
from app.infrastructure.db.models import User
from app.core.security import verify_password, get_password_hash

# Наша "база данных"
fake_users_db = {
    "pavel": {
        "id": 1,
        "username": "pavel",
        "email": "nikulin@netkam.ru",
        "hashed_password": get_password_hash("123123"),
        "is_active": True,
    }
}

def authenticate_user(email: str, password: str) -> UserInDB | None:
    """Аутентифицирует пользователя: проверяет, что такой есть и пароль верный"""
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    result = await db.execute(select(User).where(User.email == email))
    exists = result.scalar_one_or_none()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Имя пользователя уже занято",
        )

    user = User(
        hashed_password=hash_password(user.password),
        email=email,
        phone=phone,
        birthday=birthday,
        timezone=timezone
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

def user_exists(email: str):
    return UserResponse(email)