from typing import Any, Optional

from fastapi import HTTPException, status


class BaseHTTPException(HTTPException):
    """Базовое исключение для HTTP ошибок"""
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class UserAlreadyExistsError(BaseHTTPException):
    """Пользователь уже существует"""
    def __init__(self, detail: str = "User with this email already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class InvalidCredentialsError(BaseHTTPException):
    """Неверные учетные данные"""
    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class InvalidTokenError(BaseHTTPException):
    """Неверный токен"""
    def __init__(self, detail: str = "Invalid token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class TokenExpiredError(BaseHTTPException):
    """Токен истек"""
    def __init__(self, detail: str = "Token has expired"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class UserNotFoundError(BaseHTTPException):
    """Пользователь не найден"""
    def __init__(self, detail: str = "User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class PermissionDeniedError(BaseHTTPException):
    """Недостаточно прав"""
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)