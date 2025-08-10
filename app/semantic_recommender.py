from sqlalchemy.orm import Session
from .models import Review, Movie
from .semantic_embeddings import get_embedding, build_faiss_index, get_top_k_similar
from .sentiment_types import SentimentEnum
import numpy as np

def get_semantic_recommendations(db: Session, user_id: int, top_k: int = 5) -> list[str]:
    """
    Формирует рекомендации на основе семантической близости отзывов.
    """
    # Получаем положительные отзывы пользователя
    user_reviews = db.query(Review).filter(
        Review.user_id == user_id,
        Review.sentiment == SentimentEnum.positive
    ).all()

    if not user_reviews:
        return []

    # Фильмы, которые пользователь уже оценивал
    watched_movie_ids = {r.movie_id for r in user_reviews}

    # Эмбеддинги всех фильмов в базе (по среднему эмбеддингу отзывов)
    movie_embeddings = []
    movie_ids = []

    all_movies = db.query(Movie).all()
    for movie in all_movies:
        reviews = db.query(Review).filter(Review.movie_id == movie.id).all()
        if not reviews:
            continue
        emb_list = [get_embedding(r.review_text) for r in reviews]
        avg_emb = sum(emb_list) / len(emb_list)
        avg_emb = avg_emb / np.linalg.norm(avg_emb)  # нормализация
        movie_embeddings.append(avg_emb)
        movie_ids.append(movie.id)

    if not movie_embeddings:
        return []

    # Строим FAISS-индекс
    index = build_faiss_index(movie_embeddings)

    # Вектор предпочтений пользователя (среднее по его позитивным отзывам)
    user_embs = [get_embedding(r.review_text) for r in user_reviews]
    user_vector = sum(user_embs) / len(user_embs)
    user_vector = user_vector / np.linalg.norm(user_vector)

    # Поиск похожих фильмов
    top_indices = get_top_k_similar(index, user_vector, k=top_k * 2)

    # Отбираем только новые фильмы
    recommended_titles = []
    for idx in top_indices:
        movie_id = movie_ids[idx]
        if movie_id not in watched_movie_ids:
            movie = db.query(Movie).filter(Movie.id == movie_id).first()
            if movie:
                recommended_titles.append(movie.title)
        if len(recommended_titles) >= top_k:
            break

    return recommended_titles
