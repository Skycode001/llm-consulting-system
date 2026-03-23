import pytest

from app.bot.handlers import cmd_start, cmd_status, cmd_token, handle_message


@pytest.mark.asyncio
class TestHandlers:
    """Тесты для обработчиков Telegram бота"""
    
    async def test_cmd_start(self, mock_message):
        """Тест команды /start"""
        await cmd_start(mock_message)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "LLM Консультант" in call_args
        assert "/token" in call_args
    
    async def test_cmd_token_missing_token(self, mock_message):
        """Тест команды /token без токена"""
        mock_message.text = "/token"
        
        await cmd_token(mock_message)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Не указан токен" in call_args
    
    async def test_cmd_token_success(self, mock_message, mock_redis, valid_jwt_token):
        """Тест успешного сохранения токена"""
        mock_message.text = f"/token {valid_jwt_token}"
        
        await cmd_token(mock_message)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Токен сохранён" in call_args
        
        saved_token = await mock_redis.get(f"token:{mock_message.from_user.id}")
        assert saved_token == valid_jwt_token
    
    async def test_cmd_token_expired(self, mock_message, mock_redis, expired_jwt_token):
        """Тест сохранения истекшего токена"""
        mock_message.text = f"/token {expired_jwt_token}"
        
        await cmd_token(mock_message)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Токен истёк" in call_args
        
        saved_token = await mock_redis.get(f"token:{mock_message.from_user.id}")
        assert saved_token is None
    
    async def test_cmd_token_invalid(self, mock_message, mock_redis):
        """Тест сохранения неверного токена"""
        mock_message.text = "/token invalid.token.string"
        
        await cmd_token(mock_message)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Ошибка валидации" in call_args
        
        saved_token = await mock_redis.get(f"token:{mock_message.from_user.id}")
        assert saved_token is None
    
    async def test_cmd_status_no_token(self, mock_message, mock_redis):
        """Тест статуса без токена"""
        await cmd_status(mock_message)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Не авторизован" in call_args
    
    async def test_cmd_status_with_valid_token(
        self, mock_message, mock_redis, valid_jwt_token
    ):
        """Тест статуса с валидным токеном"""
        await mock_redis.set(f"token:{mock_message.from_user.id}", valid_jwt_token)
        
        await cmd_status(mock_message)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Авторизация активна" in call_args
    
    async def test_cmd_status_with_expired_token(
        self, mock_message, mock_redis, expired_jwt_token
    ):
        """Тест статуса с истекшим токеном"""
        await mock_redis.set(f"token:{mock_message.from_user.id}", expired_jwt_token)
        
        await cmd_status(mock_message)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Токен истёк" in call_args
    
    async def test_handle_message_no_token(self, mock_message, mock_redis, mock_celery):
        """Тест обработки сообщения без токена"""
        await handle_message(mock_message)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Доступ запрещён" in call_args
        mock_celery.delay.assert_not_called()
    
    async def test_handle_message_with_valid_token(
        self, mock_message, mock_redis, mock_celery, valid_jwt_token
    ):
        """Тест обработки сообщения с валидным токеном"""
        await mock_redis.set(f"token:{mock_message.from_user.id}", valid_jwt_token)
        
        await handle_message(mock_message)
        
        assert mock_message.answer.call_count == 1
        call_args = mock_message.answer.call_args[0][0]
        assert "Запрос принят" in call_args
        
        mock_celery.delay.assert_called_once_with(
            mock_message.chat.id, mock_message.text
        )
    
    async def test_handle_message_with_expired_token(
        self, mock_message, mock_redis, mock_celery, expired_jwt_token
    ):
        """Тест обработки сообщения с истекшим токеном"""
        await mock_redis.set(f"token:{mock_message.from_user.id}", expired_jwt_token)
        
        await handle_message(mock_message)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Токен истёк" in call_args
        mock_celery.delay.assert_not_called()
    
    async def test_handle_message_with_invalid_token(
        self, mock_message, mock_redis, mock_celery
    ):
        """Тест обработки сообщения с неверным токеном"""
        await mock_redis.set(f"token:{mock_message.from_user.id}", "invalid.token.string")
        
        await handle_message(mock_message)
        
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Токен невалиден" in call_args
        mock_celery.delay.assert_not_called()