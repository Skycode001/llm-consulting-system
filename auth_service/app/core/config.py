from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # App
    APP_NAME: str = Field(default="auth-service")
    ENV: str = Field(default="local")
    
    # JWT
    JWT_SECRET: str = Field(default="change_me_super_secret")
    JWT_ALG: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)
    
    # Database
    SQLITE_PATH: str = Field(default="./auth.db")
    
    @property
    def DATABASE_URL(self) -> str:
        """Получение URL базы данных"""
        return f"sqlite+aiosqlite:///{self.SQLITE_PATH}"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Создание глобального экземпляра настроек
settings = Settings()