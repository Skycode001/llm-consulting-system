from typing import AsyncGenerator, Optional

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.exceptions import InvalidTokenError, TokenExpiredError, UserNotFoundError
from app.db.session import get_db
from app.repositories.users import UserRepository
from app.schemas.user import UserPublic
from app.usecases.auth import AuthUseCase


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Зависимость для получения сессии БД"""
    async for session in get_db():
        yield session


def get_user_repository(
    session: AsyncSession = Depends(get_db_session)
) -> UserRepository:
    """Зависимость для получения репозитория пользователей"""
    return UserRepository(session)


def get_auth_usecase(
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthUseCase:
    """Зависимость для получения usecase аутентификации"""
    return AuthUseCase(user_repo)


async def get_current_user_id(
    authorization: Optional[str] = Header(None)
) -> int:
    """Зависимость для получения ID текущего пользователя из токена"""
    if not authorization:
        raise InvalidTokenError("Missing authorization header")
    
    # Проверка формата заголовка
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise InvalidTokenError("Invalid authorization header format")
    
    token = parts[1]
    
    try:
        # Декодирование токена
        payload = security.decode_token(token)
        user_id = int(payload.get("sub"))
        return user_id
    except (TokenExpiredError, InvalidTokenError):
        raise
    except (ValueError, KeyError):
        raise InvalidTokenError("Invalid token payload")


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    auth_uc: AuthUseCase = Depends(get_auth_usecase)
) -> UserPublic:
    """Зависимость для получения текущего пользователя"""
    try:
        user = await auth_uc.get_current_user(user_id)
        return user
    except UserNotFoundError:
        raise InvalidTokenError("User not found")