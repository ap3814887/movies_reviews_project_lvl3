"""
crud.py - функции для создания и получения данных из базы.
"""
from typing import Optional
from sqlalchemy.orm import Session

from . import models

from .sentiment_types import SentimentEnum
from .sentiment import classify_sentiment



def get_or_create_movie(db: Session, title: str) -> models.Movie:
    """
    Получает фильм по названию из БД, если он существует, иначе — создаёт новый фильм и возвращает его.

    Args:
        db (Session): текущая сессия БД.
        title (str): название фильма.

    Returns:
        Movie: экземпляр модели Movie.
    """
    # Поиск фильма по названию
    movie = db.query(models.Movie).filter(models.Movie.title == title).first()

    if movie is None:
        # Если фильм не найден — создаём новый
        movie = models.Movie(title=title)
        db.add(movie)     # Добавляем в сессию
        db.commit()       # Фиксируем изменения
        db.refresh(movie) # Обновляем объект из БД

    return movie


def create_review(db: Session, movie_id: int, rating: int, review_text: str, sentiment: str, user_id: int) -> models.Review:
    sentiment = classify_sentiment(review_text)
    review = models.Review(movie_id=movie_id, rating=rating, review_text=review_text, sentiment=sentiment, user_id=user_id)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review



def get_reviews(db: Session, movie_filter: Optional[str] = None, sentiment_filter: Optional[str] = None) -> list[models.Review]:
    """
    Получает список всех отзывов, с возможностью фильтрации по названию фильма.

    Args:
        db (Session): текущая сессия БД.
        movie_filter (str, optional): строка для фильтрации названия фильма.

    Returns:
        list[Review]: список отзывов, удовлетворяющих условиям.
    """
    # Начальный запрос: объединение отзывов и фильмов
    query = db.query(models.Review).join(models.Movie)

    # Если указана фильтрация по названию фильма (регистр — не важен)
    if movie_filter:
        query = query.filter(models.Movie.title.ilike(f"%{movie_filter}%"))

    if sentiment_filter:
        try:
            sentiment_enum = SentimentEnum(sentiment_filter.lower())
            query = query.filter(models.Review.sentiment == sentiment_enum)
        except ValueError:
            return [] # некорректный фильтр по тональности


    return query.all()
