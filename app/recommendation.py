from sqlalchemy.orm import Session
from .models import Review, Movie
from collections import Counter
from .sentiment_types import SentimentEnum

def recommend_movies_for_user(user_id: int, db: Session, top_k=5) -> list[str]:
    # Получаем фильмы, которые пользователь уже оценил (любые отзывы)
    watched_movie_ids = set(
        r.movie_id for r in db.query(Review).filter_by(user_id=user_id).all()
    )
    
    # Получаем все положительные отзывы всех пользователей
    positive_reviews = db.query(Review).filter_by(sentiment=SentimentEnum.positive).all()
    
    # Считаем популярность фильмов среди всех пользователей
    popular_movies_counter = Counter(r.movie.title for r in positive_reviews)
    
    # Исключаем фильмы, которые пользователь уже смотрел
    for watched_id in watched_movie_ids:
        movie = db.query(Movie).filter_by(id=watched_id).first()
        if movie and movie.title in popular_movies_counter:
            del popular_movies_counter[movie.title]
    
    # Возвращаем топ-K популярных фильмов, которые пользователь не смотрел
    top_movies = [movie for movie, _ in popular_movies_counter.most_common(top_k)]
    return top_movies
