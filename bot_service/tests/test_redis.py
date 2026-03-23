import pytest

from app.infra.redis import close_redis, delete_token, get_redis, get_token, save_token


@pytest.mark.asyncio
class TestRedis:
    """Тесты для Redis операций"""
    
    async def test_get_redis_returns_client(self, mock_redis):
        """Тест получения клиента Redis"""
        client = await get_redis()
        assert client is not None
    
    async def test_save_and_get_token(self, mock_redis):
        """Тест сохранения и получения токена"""
        tg_user_id = 12345
        jwt_token = "test.jwt.token"
        
        await save_token(tg_user_id, jwt_token)
        saved_token = await get_token(tg_user_id)
        
        assert saved_token == jwt_token
    
    async def test_save_token_with_ttl(self, mock_redis):
        """Тест сохранения токена с TTL"""
        tg_user_id = 12345
        jwt_token = "test.jwt.token"
        ttl = 60
        
        await save_token(tg_user_id, jwt_token, ttl_seconds=ttl)
        
        ttl_remaining = await mock_redis.ttl(f"token:{tg_user_id}")
        assert ttl_remaining <= ttl
        assert ttl_remaining > 0
    
    async def test_get_nonexistent_token(self, mock_redis):
        """Тест получения несуществующего токена"""
        token = await get_token(99999)
        assert token is None
    
    async def test_delete_token(self, mock_redis):
        """Тест удаления токена"""
        tg_user_id = 12345
        jwt_token = "test.jwt.token"
        
        await save_token(tg_user_id, jwt_token)
        await delete_token(tg_user_id)
        
        saved_token = await get_token(tg_user_id)
        assert saved_token is None
    
    async def test_close_redis(self, mock_redis):
        """Тест закрытия соединения Redis"""
        await close_redis()
        
        client = await get_redis()
        assert client is not None