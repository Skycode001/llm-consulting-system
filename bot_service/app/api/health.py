from fastapi import APIRouter

from app.core.config import settings
from app.infra.celery_app import celery_app
from app.infra.redis import get_redis

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check():
    """
    Проверка здоровья сервиса
    """
    redis_status = "ok"
    rabbitmq_status = "ok"
    
    try:
        redis_client = await get_redis()
        await redis_client.ping()
    except Exception as e:
        redis_status = f"error: {str(e)}"
    
    try:
        celery_app.control.ping(timeout=1.0)
    except Exception as e:
        rabbitmq_status = f"error: {str(e)}"
    
    return {
        "service": settings.APP_NAME,
        "environment": settings.ENV,
        "status": "healthy" if redis_status == "ok" and rabbitmq_status == "ok" else "degraded",
        "components": {
            "redis": redis_status,
            "rabbitmq": rabbitmq_status,
            "celery": rabbitmq_status
        }
    }


@router.get("/redis")
async def redis_health():
    """
    Проверка здоровья Redis
    """
    try:
        redis_client = await get_redis()
        await redis_client.ping()
        return {"status": "ok", "service": "redis"}
    except Exception as e:
        return {"status": "error", "service": "redis", "error": str(e)}


@router.get("/rabbitmq")
async def rabbitmq_health():
    """
    Проверка здоровья RabbitMQ
    """
    try:
        celery_app.control.ping(timeout=1.0)
        return {"status": "ok", "service": "rabbitmq"}
    except Exception as e:
        return {"status": "error", "service": "rabbitmq", "error": str(e)}