from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int =5432
    POSTGRES_USER: str = "task_user"
    POSTGRES_PASSWORD: str = "task_secret"
    POSTGRES_DB: str = "task_db"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
    # REDIS_URL: str = "redis://localhost:6379"
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