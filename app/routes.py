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
from .recommendation import recommend_movies_for_user

from fastapi import Depends, HTTPException, status
from .auth import get_current_user
from . import models
from .models import User
from . import auth
from fastapi.security import OAuth2PasswordRequestForm

from .semantic_recommender import get_semantic_recommendations

from .clustering import cluster_movies_by_reviews

from .collaborative_filtering import collaborative_filtering_recommendations

router = APIRouter()

@router.post("/register", response_model=schemas.UserRead)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = auth.hash_password(user_in.password)
    user = User(name=user_in.name, email=user_in.email, hashed_password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return schemas.UserRead(id=user.id, name=user.name, email=user.email)

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# Пример защищенного эндпоинта:
@router.get("/me", response_model=schemas.UserRead)
def read_users_me(current_user: User = Depends(auth.get_current_user)):
    return schemas.UserRead(id=current_user.id, name=current_user.name, email=current_user.email)


@router.get("/semantic-recommendations", response_model=List[str])
def semantic_recommendation_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_semantic_recommendations(db, user_id=current_user.id)

@router.post("/reviews", response_model=schemas.ReviewRead)
def create_review_endpoint(
    review_in: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) 
) -> schemas.ReviewRead:
    movie = crud.get_or_create_movie(db, review_in.movie_title)
    sentiment = classify_sentiment(review_in.review_text)

    # Теперь передаём user_id текущего пользователя
    review = crud.create_review(db, movie.id, review_in.rating, review_in.review_text, sentiment, current_user.id)

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    
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
@router.get("/recommendations", response_model=List[str])
def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return recommend_movies_for_user(current_user.id, db)

@router.get("/clustered-movies")
def get_clustered_movies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    clusters = cluster_movies_by_reviews(db)
    return clusters

@router.get("/collaborative-recommendations", response_model=List[str])
def get_collaborative_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return collaborative_filtering_recommendations(db, current_user.id)