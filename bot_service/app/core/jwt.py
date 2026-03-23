from typing import Any, Dict

from jose import jwt

from app.core.config import settings


class JWTValidationError(Exception):
    """Ошибка валидации JWT токена"""
    pass


class JWTExpiredError(JWTValidationError):
    """Токен истек"""
    pass


def decode_and_validate(token: str) -> Dict[str, Any]:
    """
    Декодирование и валидация JWT токена
    
    Args:
        token: JWT токен в формате строки
        
    Returns:
        Payload токена в виде словаря
        
    Raises:
        JWTValidationError: если токен невалидный
        JWTExpiredError: если токен истек
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG]
        )
        
        if "sub" not in payload:
            raise JWTValidationError("Token missing 'sub' claim")
        
        if "role" not in payload:
            raise JWTValidationError("Token missing 'role' claim")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise JWTExpiredError("Token has expired")
    except jwt.JWTError as e:
        raise JWTValidationError(f"Invalid token: {str(e)}")


def extract_user_id(token: str) -> str:
    """
    Извлечение user_id из токена
    
    Args:
        token: JWT токен
        
    Returns:
        user_id из поля sub
    """
    payload = decode_and_validate(token)
    return payload.get("sub")


def extract_role(token: str) -> str:
    """
    Извлечение роли пользователя из токена
    
    Args:
        token: JWT токен
        
    Returns:
        роль пользователя
    """
    payload = decode_and_validate(token)
    return payload.get("role", "user")