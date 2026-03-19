import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# Создание тестовой БД
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_auth.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool
)

TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def override_get_db():
    """Переопределение зависимости get_db для тестов"""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_database():
    """Фикстура для настройки тестовой БД"""
    # Создание таблиц
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Очистка после тестов
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
class TestAuthAPI:
    """Интеграционные тесты для Auth API"""
    
    async def test_register_user_success(self):
        """Тест успешной регистрации"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as ac:
            response = await ac.post(
                "/api/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "password123"
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["email"] == "test@example.com"
            assert "id" in data
            assert data["role"] == "user"
    
    async def test_register_duplicate_email(self):
        """Тест регистрации с существующим email"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as ac:
            # Первая регистрация
            await ac.post(
                "/api/auth/register",
                json={
                    "email": "duplicate@example.com",
                    "password": "password123"
                }
            )
            
            # Попытка повторной регистрации
            response = await ac.post(
                "/api/auth/register",
                json={
                    "email": "duplicate@example.com",
                    "password": "password123"
                }
            )
            
            assert response.status_code == 409
            assert "already exists" in response.json()["detail"].lower()
    
    async def test_login_success(self):
        """Тест успешного входа"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as ac:
            # Регистрация
            await ac.post(
                "/api/auth/register",
                json={
                    "email": "login@example.com",
                    "password": "password123"
                }
            )
            
            # Логин
            response = await ac.post(
                "/api/auth/login",
                data={
                    "username": "login@example.com",
                    "password": "password123"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
    
    async def test_login_wrong_password(self):
        """Тест входа с неверным паролем"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as ac:
            # Регистрация
            await ac.post(
                "/api/auth/register",
                json={
                    "email": "wrong@example.com",
                    "password": "password123"
                }
            )
            
            # Логин с неверным паролем
            response = await ac.post(
                "/api/auth/login",
                data={
                    "username": "wrong@example.com",
                    "password": "wrong_password"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            assert response.status_code == 401
    
    async def test_get_me_with_token(self):
        """Тест получения профиля с валидным токеном"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as ac:
            # Регистрация
            await ac.post(
                "/api/auth/register",
                json={
                    "email": "me@example.com",
                    "password": "password123"
                }
            )
            
            # Логин
            login_response = await ac.post(
                "/api/auth/login",
                data={
                    "username": "me@example.com",
                    "password": "password123"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            token = login_response.json()["access_token"]
            
            # Получение профиля
            response = await ac.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "me@example.com"
    
    async def test_get_me_without_token(self):
        """Тест получения профиля без токена"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as ac:
            response = await ac.get("/api/auth/me")
            assert response.status_code == 401