from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api import deps
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.usecases.auth import AuthUseCase

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя"
)
async def register(
    register_data: RegisterRequest,
    auth_uc: AuthUseCase = Depends(deps.get_auth_usecase)
):
    """
    Регистрация нового пользователя в системе
    
    - **email**: email пользователя (должен быть уникальным)
    - **password**: пароль (минимум 6 символов)
    """
    return await auth_uc.register(register_data.email, register_data.password)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Вход в систему"
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_uc: AuthUseCase = Depends(deps.get_auth_usecase)
):
    """
    Вход в систему и получение JWT токена
    
    - **username**: email пользователя
    - **password**: пароль
    """
    return await auth_uc.login(form_data.username, form_data.password)


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Информация о текущем пользователе"
)
async def get_me(
    current_user: UserPublic = Depends(deps.get_current_user)
):
    """
    Получение информации о текущем пользователе
    """
    return current_user