from fastapi import APIRouter

from app.api.routes_auth import router as auth_router

# Создание главного роутера
api_router = APIRouter(prefix="/api")

# Подключение роутеров
api_router.include_router(auth_router)