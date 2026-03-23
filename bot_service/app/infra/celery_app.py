from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "bot_service",
    broker=settings.RABBITMQ_URL,
    backend="rpc://",  # Используем RPC бэкенд для получения результатов
    include=["app.tasks.llm_tasks"]  # Автоматическая загрузка задач
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=60 * 5,  # 5 минут
    task_soft_time_limit=60 * 4,  # 4 минуты
    broker_connection_retry_on_startup=True,
)