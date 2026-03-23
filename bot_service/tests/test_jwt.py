from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.config import settings
from app.core.jwt import (
    JWTExpiredError,
    JWTValidationError,
    decode_and_validate,
    extract_role,
    extract_user_id,
)


class TestJWTValidation:
    """Тесты для JWT валидации"""
    
    def test_decode_valid_token(self):
        """Тест декодирования валидного токена"""
        payload = {
            "sub": "12345",
            "role": "user",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc)
        }
        
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        result = decode_and_validate(token)
        
        assert result["sub"] == "12345"
        assert result["role"] == "user"
        assert "exp" in result
        assert "iat" in result
    
    def test_decode_expired_token_raises_error(self):
        """Тест декодирования истекшего токена"""
        payload = {
            "sub": "12345",
            "role": "user",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            "iat": datetime.now(timezone.utc) - timedelta(hours=2)
        }
        
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        
        with pytest.raises(JWTExpiredError):
            decode_and_validate(token)
    
    def test_decode_invalid_token_raises_error(self):
        """Тест декодирования неверного токена"""
        invalid_token = "invalid.token.string"
        
        with pytest.raises(JWTValidationError):
            decode_and_validate(invalid_token)
    
    def test_decode_token_missing_sub_raises_error(self):
        """Тест декодирования токена без поля sub"""
        payload = {
            "role": "user",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc)
        }
        
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        
        with pytest.raises(JWTValidationError) as exc_info:
            decode_and_validate(token)
        
        assert "missing 'sub'" in str(exc_info.value).lower()
    
    def test_decode_token_missing_role_raises_error(self):
        """Тест декодирования токена без поля role"""
        payload = {
            "sub": "12345",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc)
        }
        
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        
        with pytest.raises(JWTValidationError) as exc_info:
            decode_and_validate(token)
        
        assert "missing 'role'" in str(exc_info.value).lower()
    
    def test_extract_user_id(self):
        """Тест извлечения user_id из токена"""
        payload = {
            "sub": "12345",
            "role": "user",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc)
        }
        
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        user_id = extract_user_id(token)
        
        assert user_id == "12345"
    
    def test_extract_role(self):
        """Тест извлечения роли из токена"""
        payload = {
            "sub": "12345",
            "role": "admin",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc)
        }
        
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        role = extract_role(token)
        
        assert role == "admin"
    
    def test_extract_role_default(self):
        """Тест извлечения роли с значением по умолчанию"""
        payload = {
            "sub": "12345",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc)
        }
        
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        
        with pytest.raises(JWTValidationError):
            extract_role(token)