from datetime import timedelta

import pytest
from jose import jwt

from app.core.config import settings
from app.core.exceptions import InvalidTokenError, TokenExpiredError
from app.core.security import create_access_token, decode_token, hash_password, verify_password


class TestPasswordHashing:
    """Тесты для хеширования паролей"""
    
    def test_hash_password_returns_string(self):
        """Проверка, что хеш возвращается как строка"""
        password = "test_password123"
        hashed = hash_password(password)
        
        assert isinstance(hashed, str)
        assert hashed != password
    
    def test_verify_password_correct(self):
        """Проверка правильного пароля"""
        password = "test_password123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Проверка неправильного пароля"""
        password = "test_password123"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False


class TestJWTToken:
    """Тесты для JWT токенов"""
    
    def test_create_token_contains_required_fields(self):
        """Проверка, что токен содержит все обязательные поля"""
        user_id = 1
        role = "user"
        
        token = create_access_token(data={"sub": user_id, "role": role})
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        
        assert str(user_id) == payload["sub"]
        assert role == payload["role"]
        assert "exp" in payload
        assert "iat" in payload
    
    def test_decode_valid_token(self):
        """Проверка декодирования валидного токена"""
        user_id = 123
        role = "admin"
        
        token = create_access_token(data={"sub": user_id, "role": role})
        payload = decode_token(token)
        
        assert str(user_id) == payload["sub"]
        assert role == payload["role"]
    
    def test_decode_expired_token_raises_error(self):
        """Проверка, что истекший токен вызывает ошибку"""
        # Токен с истекшим сроком действия
        expired_delta = timedelta(seconds=-1)
        token = create_access_token(
            data={"sub": "1", "role": "user"},
            expires_delta=expired_delta
        )
        
        with pytest.raises(TokenExpiredError):
            decode_token(token)
    
    def test_decode_invalid_token_raises_error(self):
        """Проверка, что неверный токен вызывает ошибку"""
        invalid_token = "invalid.token.string"
        
        with pytest.raises(InvalidTokenError):
            decode_token(invalid_token)