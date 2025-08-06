"""
models.py

SQLAlchemy ORM-модели: Movie и Review.
"""

from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, func, Enum

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

from .sentiment_types import SentimentEnum

class Movie(Base):
    __tablename__ = "movies"  # Название таблицы в базе данных

    # Уникальный идентификатор фильма (первичный ключ)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Название фильма, должно быть уникальным и не null
    title: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    
    # Дата и время создания записи, по умолчанию — текущее время
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    # Отношение "один-ко-многим": один фильм может иметь несколько отзывов
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="movie")

class Review(Base):
    __tablename__ = "reviews"  # Название таблицы в базе данных

    # Уникальный идентификатор отзыва (первичный ключ)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Внешний ключ — ID фильма, на который оставлен отзыв
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"))

    # Оценка фильма (от 1 до 10), не может быть пустой
    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    # Текст отзыва (обязательное поле)
    review_text: Mapped[str] = mapped_column(Text, nullable=False)

    sentiment: Mapped[SentimentEnum] = mapped_column(Enum(SentimentEnum), nullable=False)

    # Дата и время создания отзыва, по умолчанию — текущее время
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    # Обратное отношение к фильму — ссылка на объект Movie
    movie: Mapped[Movie] = relationship("Movie", back_populates="reviews")
