from typing import Optional

import redis.asyncio as redis

from app.core.config import settings

_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """
    Получение клиента Redis (синглтон)
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            encoding="utf-8"
        )
    return _redis_client


async def close_redis():
    """Закрытие соединения с Redis"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


async def save_token(tg_user_id: int, jwt_token: str, ttl_seconds: int = 3600):
    """
    Сохранение JWT токена в Redis для пользователя Telegram
    
    Args:
        tg_user_id: ID пользователя в Telegram
        jwt_token: JWT токен
        ttl_seconds: время жизни токена в секундах (по умолчанию 1 час)
    """
    redis_client = await get_redis()
    key = f"token:{tg_user_id}"
    await redis_client.setex(key, ttl_seconds, jwt_token)


async def get_token(tg_user_id: int) -> Optional[str]:
    """
    Получение JWT токена из Redis для пользователя Telegram
    
    Args:
        tg_user_id: ID пользователя в Telegram
        
    Returns:
        JWT токен или None если не найден
    """
    redis_client = await get_redis()
    key = f"token:{tg_user_id}"
    return await redis_client.get(key)


async def delete_token(tg_user_id: int):
    """
    Удаление JWT токена из Redis
    
    Args:
        tg_user_id: ID пользователя в Telegram
    """
    redis_client = await get_redis()
    key = f"token:{tg_user_id}"
    await redis_client.delete(key)