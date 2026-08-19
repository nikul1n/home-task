from app.schemas.user import UserInDB
from app.core.security import verify_password, get_password_hash

# Наша "база данных"
fake_users_db = {
    "alex": {
        "id": 1,
        "username": "alex",
        "email": "alex@example.com",
        "hashed_password": get_password_hash("secret123"),
        "is_active": True,
    }
}

def get_user_by_useremail(email: str) -> UserInDB | None:
    """Ищет пользователя по email"""
    if email in fake_users_db:
        return UserInDB(**fake_users_db[email])
    return None

def authenticate_user(email: str, password: str) -> UserInDB | None:
    """Аутентифицирует пользователя: проверяет, что такой есть и пароль верный"""
    user = get_user_by_useremail(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user