from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr


class UserCreate(UserBase):
    """Схема создания пользователя"""
    password: str
    role: str = "user"


class UserPublic(UserBase):
    """Публичная информация о пользователе"""
    id: int
    role: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserPublic):
    """Пользователь в БД (с хешем пароля)"""
    password_hash: str
    
    model_config = ConfigDict(from_attributes=True)