
from app.core import security
from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError, UserNotFoundError
from app.repositories.users import UserRepository
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate, UserPublic


class AuthUseCase:
    """Бизнес-логика аутентификации"""
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def register(self, email: str, password: str) -> UserPublic:
        """Регистрация нового пользователя"""
        # Проверка, существует ли пользователь
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError()
        
        # Создание пользователя
        password_hash = security.hash_password(password)
        user_data = UserCreate(email=email, password=password, role="user")
        user = await self.user_repo.create(user_data, password_hash)
        
        return UserPublic.model_validate(user)
    
    async def login(self, email: str, password: str) -> TokenResponse:
        """Вход пользователя"""
        # Поиск пользователя
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise InvalidCredentialsError()
        
        # Проверка пароля
        if not security.verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        
        # Создание токена
        access_token = security.create_access_token(
            data={"sub": str(user.id), "role": user.role}
        )
        
        return TokenResponse(access_token=access_token)
    
    async def get_current_user(self, user_id: int) -> UserPublic:
        """Получение текущего пользователя"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        return UserPublic.model_validate(user)