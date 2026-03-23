from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""
    
    APP_NAME: str = Field(default="bot-service")
    ENV: str = Field(default="local")
    
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram bot token from @BotFather")
    
    JWT_SECRET: str = Field(default="change_me_super_secret")
    JWT_ALG: str = Field(default="HS256")
    
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    RABBITMQ_URL: str = Field(default="amqp://guest:guest@localhost:5672//")
    
    OPENROUTER_API_KEY: str = Field(..., description="OpenRouter API key")
    OPENROUTER_BASE_URL: str = Field(default="https://openrouter.ai/api/v1")
    OPENROUTER_MODEL: str = Field(default="stepfun/step-3.5-flash:free")
    OPENROUTER_SITE_URL: str = Field(default="https://example.com")
    OPENROUTER_APP_NAME: str = Field(default="bot-service")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()