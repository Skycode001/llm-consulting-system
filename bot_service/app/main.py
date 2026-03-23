from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения
    """
    print(f"Starting {settings.APP_NAME} in {settings.ENV} mode")
    print(f"Redis: {settings.REDIS_URL}")
    print(f"RabbitMQ: {settings.RABBITMQ_URL}")
    
    yield
    
    print(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Bot Service with Telegram bot, Celery, RabbitMQ, Redis, OpenRouter",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENV != "production" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "service": settings.APP_NAME,
        "version": "0.1.0",
        "status": "running"
    }