import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
class TestHealthAPI:
    """Тесты для health check эндпоинтов"""
    
    async def test_health_endpoint(self):
        """Тест эндпоинта /health"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "bot-service"
            assert "status" in data
            assert "components" in data
    
    async def test_root_endpoint(self):
        """Тест корневого эндпоинта"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/")
            
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "bot-service"
            assert data["status"] == "running"