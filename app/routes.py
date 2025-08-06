"""
routes.py

Эндпоинты FastAPI для отзывов о фильмах.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from . import schemas, crud
from .database import get_db

from .sentiment import classify_sentiment

router = APIRouter()


@router.post("/reviews", response_model=schemas.ReviewRead)
def create_review_endpoint(
    review_in: schemas.ReviewCreate,
    db: Session = Depends(get_db)
) -> schemas.ReviewRead:
    # Получаем или создаём фильм по названию (если не найден)
    movie = crud.get_or_create_movie(db, review_in.movie_title)

    sentimet = classify_sentiment(review_in.review_text)
    
    # Создаём отзыв, связанный с фильмом
    review = crud.create_review(db, movie.id, review_in.rating, review_in.review_text, sentiment=sentimet)

    # Возвращаем результат в формате схемы ReviewRead
    return schemas.ReviewRead(
        id=review.id,
        movie_title=movie.title,
        rating=review.rating,
        review_text=review.review_text,
        sentiment=review.sentiment,
        created_at=review.created_at,
    )


@router.get("/reviews", response_model=List[schemas.ReviewRead])
def list_reviews_endpoint(
    movie: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> List[schemas.ReviewRead]:
    # Получаем список отзывов (при наличии фильтра — только по фильму)
    reviews = crud.get_reviews(db, movie_filter=movie, sentiment_filter=sentiment)

    # Преобразуем объекты SQLAlchemy в Pydantic-схемы
    return [
        schemas.ReviewRead(
            id=r.id,
            movie_title=r.movie.title,
            rating=r.rating,
            review_text=r.review_text,
            sentiment=r.sentiment,
            created_at=r.created_at
        )
        for r in reviews
    ]
