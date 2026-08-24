from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://family_user:family_password@localhost/family_db"
    REDIS_URL: str = "redis://localhost:6379"
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # model_config = ConfigDict(
    #     env_file=".env",          # для локальной разработки
    #     case_sensitive=False,     # имена переменных не чувствительны к регистру
    # )

    class Config:
        env_file = ".env"
        extra="ignore"

settings = Settings()