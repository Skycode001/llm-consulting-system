from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения
    """
    # Startup
    print(f"Starting {settings.APP_NAME} in {settings.ENV} mode")
    
    # Создание таблиц в БД (только для разработки)
    if settings.ENV == "local":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    print(f"Shutting down {settings.APP_NAME}")
    await engine.dispose()


# Создание приложения FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Auth Service for JWT authentication",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENV != "production" else None,
    redoc_url=None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(api_router)


@app.get("/health", tags=["System"])
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.ENV
    }