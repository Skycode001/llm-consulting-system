from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

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
    swagger_ui_parameters={
        "persistAuthorization": True,
    }
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


# Настройка OpenAPI для авторизации
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Добавляем схему безопасности для Bearer токена
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Введите JWT токен в формате: Bearer <token>"
        }
    }
    
    # Применяем безопасность только к эндпоинтам, которые требуют авторизацию
    # Исключаем /health, /api/auth/register, /api/auth/login
    public_paths = ["/health", "/api/auth/register", "/api/auth/login"]
    
    for path in openapi_schema["paths"]:
        # Проверяем, не является ли путь публичным
        is_public = False
        for public_path in public_paths:
            if path.startswith(public_path):
                is_public = True
                break
        
        if not is_public:
            for method in openapi_schema["paths"][path]:
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi