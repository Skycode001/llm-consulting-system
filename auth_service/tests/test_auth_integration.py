import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.api.deps as deps_module
import app.db.session as db_session_module
from app.db.base import Base
from app.main import app


@pytest.mark.asyncio
async def test_register_user_success():
    """Тест успешной регистрации"""
    print("\n=== START TEST: test_register_user_success ===")
    
    # Создаем in-memory базу
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    
    # Сохраняем оригинальные функции
    original_db_session_get_db = db_session_module.get_db
    original_deps_get_db = deps_module.get_db
    
    # Переопределяем get_db
    db_session_module.get_db = override_get_db
    deps_module.get_db = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "password123"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["role"] == "user"
    
    # Восстанавливаем
    db_session_module.get_db = original_db_session_get_db
    deps_module.get_db = original_deps_get_db
    
    await engine.dispose()
    print("=== END TEST: test_register_user_success ===")


@pytest.mark.asyncio
async def test_register_duplicate_email():
    """Тест регистрации с существующим email"""
    print("\n=== START TEST: test_register_duplicate_email ===")
    
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    
    original_db_session_get_db = db_session_module.get_db
    original_deps_get_db = deps_module.get_db
    
    db_session_module.get_db = override_get_db
    deps_module.get_db = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Первая регистрация
        response1 = await client.post(
            "/api/auth/register",
            json={"email": "duplicate@example.com", "password": "password123"}
        )
        assert response1.status_code == 201
        
        # Попытка повторной регистрации
        response2 = await client.post(
            "/api/auth/register",
            json={"email": "duplicate@example.com", "password": "password123"}
        )
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"].lower()
    
    db_session_module.get_db = original_db_session_get_db
    deps_module.get_db = original_deps_get_db
    
    await engine.dispose()
    print("=== END TEST: test_register_duplicate_email ===")


@pytest.mark.asyncio
async def test_login_success():
    """Тест успешного входа"""
    print("\n=== START TEST: test_login_success ===")
    
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    
    original_db_session_get_db = db_session_module.get_db
    original_deps_get_db = deps_module.get_db
    
    db_session_module.get_db = override_get_db
    deps_module.get_db = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Регистрация
        await client.post(
            "/api/auth/register",
            json={"email": "login@example.com", "password": "password123"}
        )
        
        # Логин
        response = await client.post(
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
    
    db_session_module.get_db = original_db_session_get_db
    deps_module.get_db = original_deps_get_db
    
    await engine.dispose()
    print("=== END TEST: test_login_success ===")


@pytest.mark.asyncio
async def test_login_wrong_password():
    """Тест входа с неверным паролем"""
    print("\n=== START TEST: test_login_wrong_password ===")
    
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    
    original_db_session_get_db = db_session_module.get_db
    original_deps_get_db = deps_module.get_db
    
    db_session_module.get_db = override_get_db
    deps_module.get_db = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Регистрация
        await client.post(
            "/api/auth/register",
            json={"email": "wrong@example.com", "password": "password123"}
        )
        
        # Логин с неверным паролем
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "wrong@example.com",
                "password": "wrong_password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
    
    db_session_module.get_db = original_db_session_get_db
    deps_module.get_db = original_deps_get_db
    
    await engine.dispose()
    print("=== END TEST: test_login_wrong_password ===")


@pytest.mark.asyncio
async def test_get_me_with_token():
    """Тест получения профиля с валидным токеном"""
    print("\n=== START TEST: test_get_me_with_token ===")
    
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    
    original_db_session_get_db = db_session_module.get_db
    original_deps_get_db = deps_module.get_db
    
    db_session_module.get_db = override_get_db
    deps_module.get_db = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Регистрация
        await client.post(
            "/api/auth/register",
            json={"email": "me@example.com", "password": "password123"}
        )
        
        # Логин
        login_response = await client.post(
            "/api/auth/login",
            data={
                "username": "me@example.com",
                "password": "password123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]
        
        # Получение профиля
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@example.com"
    
    db_session_module.get_db = original_db_session_get_db
    deps_module.get_db = original_deps_get_db
    
    await engine.dispose()
    print("=== END TEST: test_get_me_with_token ===")


@pytest.mark.asyncio
async def test_get_me_without_token():
    """Тест получения профиля без токена"""
    print("\n=== START TEST: test_get_me_without_token ===")
    
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    
    original_db_session_get_db = db_session_module.get_db
    original_deps_get_db = deps_module.get_db
    
    db_session_module.get_db = override_get_db
    deps_module.get_db = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/auth/me")
        assert response.status_code == 401
    
    db_session_module.get_db = original_db_session_get_db
    deps_module.get_db = original_deps_get_db
    
    await engine.dispose()
    print("=== END TEST: test_get_me_without_token ===")