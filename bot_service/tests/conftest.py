from unittest.mock import AsyncMock, MagicMock, patch

import fakeredis.aioredis
import pytest
from aiogram import Bot
from aiogram.types import Message

from app.core.config import settings


@pytest.fixture
def mock_redis():
    """Фикстура для мока Redis с использованием fakeredis"""
    redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    
    with patch("app.infra.redis.get_redis") as mock_get_redis:
        mock_get_redis.return_value = redis_client
        yield redis_client


@pytest.fixture
def mock_celery():
    """Фикстура для мока Celery задач"""
    with patch("app.bot.handlers.llm_request") as mock_task:
        yield mock_task


@pytest.fixture
def mock_openrouter_success():
    """Фикстура для мока успешного ответа OpenRouter"""
    with patch("app.services.openrouter_client.call_openrouter") as mock:
        mock.return_value = {
            "success": True,
            "content": "Это тестовый ответ от LLM"
        }
        yield mock


@pytest.fixture
def mock_openrouter_error():
    """Фикстура для мока ошибки OpenRouter"""
    with patch("app.services.openrouter_client.call_openrouter") as mock:
        mock.return_value = {
            "success": False,
            "error": "OpenRouter API error"
        }
        yield mock


@pytest.fixture
def valid_jwt_token():
    """Фикстура для валидного JWT токена"""
    from datetime import datetime, timedelta, timezone

    from jose import jwt
    
    payload = {
        "sub": "12345",
        "role": "user",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc)
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    return token


@pytest.fixture
def expired_jwt_token():
    """Фикстура для истекшего JWT токена"""
    from datetime import datetime, timedelta, timezone

    from jose import jwt
    
    payload = {
        "sub": "12345",
        "role": "user",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        "iat": datetime.now(timezone.utc) - timedelta(hours=2)
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    return token


@pytest.fixture
def mock_message():
    """Фикстура для мока сообщения Telegram"""
    message = MagicMock(spec=Message)
    message.from_user = MagicMock()
    message.from_user.id = 123456789
    message.text = "Тестовое сообщение"
    message.chat = MagicMock()
    message.chat.id = 987654321
    message.answer = AsyncMock()
    return message


@pytest.fixture
def mock_bot():
    """Фикстура для мока бота"""
    bot = MagicMock(spec=Bot)
    return bot