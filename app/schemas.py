"""
schemas.py

Pydantic-схемы для валидации запросов и ответов.
"""
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr  

from .sentiment_types import SentimentEnum


class ReviewCreate(BaseModel):
    movie_title: str = Field(..., min_length=1)     # Название фильма (обязательно, минимум 1 символ)
    review_text: str = Field(..., min_length=1)     # Текст отзыва (обязательно, минимум 1 символ)
    rating: int = Field(..., ge=1, le=10)           # Оценка (целое число от 1 до 10)


class ReviewRead(BaseModel):
    id: int                          # Уникальный ID отзыва
    movie_title: str                 # Название фильма
    rating: int                      # Оценка отзыва
    review_text: str                 # Содержание отзыва
    sentiment: SentimentEnum
    created_at: datetime             # Время создания

# Схема регистрации пользователя
class UserCreate(BaseModel):
    name: str
    email: EmailStr 
    password: str

# Схема для возврата данных пользователя
class UserRead(BaseModel):
    id: int
    name: str
    email: str

# Для возврата JWT-токена
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


    class Config:
        from_attributes = True       # Позволяет строить объект из ORM-моделей SQLAlchemy


