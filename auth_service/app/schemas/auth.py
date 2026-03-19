from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Схема запроса на регистрацию"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=6, description="Пароль (минимум 6 символов)")


class LoginResponse(BaseModel):
    """Схема ответа при успешном входе"""
    access_token: str
    token_type: str = "bearer"


class TokenResponse(LoginResponse):
    """Схема ответа с токеном (алиас для LoginResponse)"""
    pass


class TokenData(BaseModel):
    """Данные из токена"""
    sub: str
    role: str = "user"
    exp: int
    iat: int