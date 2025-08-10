import pandas as pd
from sqlalchemy.orm import Session
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from .models import Review

def collaborative_filtering_recommendations(db: Session, user_id: int, top_n: int = 5, similarity_threshold: float = 0.3, min_user_ratings=2, min_movie_ratings=2) -> list[str]:
    """
    Коллаборативная фильтрация с фильтрацией по активности и порогом схожести.
    
    Args:
        db: Сессия базы данных.
        user_id: ID пользователя, для которого делаем рекомендации.
        top_n: Количество рекомендаций.
        similarity_threshold: Минимальный порог сходства для учёта пользователя.
        min_user_ratings: Минимальное число оценок у пользователя для участия.
        min_movie_ratings: Минимальное число оценок у фильма для участия.
    
    Returns:
        Список названий фильмов для рекомендации.
    """
        
    reviews = db.query(Review).all()
    if not reviews:
        return []

    data = [{"user_id": r.user_id, "movie_title": r.movie.title, "rating": r.rating} for r in reviews]
    df = pd.DataFrame(data)
    
    # Фильтруем малоактивных пользователей и малооцененные фильмы
    user_counts = df['user_id'].value_counts()
    movie_counts = df['movie_title'].value_counts()

    df = df[df['user_id'].isin(user_counts[user_counts >= min_user_ratings].index)]
    df = df[df['movie_title'].isin(movie_counts[movie_counts >= min_movie_ratings].index)]

    user_movie_matrix = df.pivot_table(index='user_id', columns='movie_title', values='rating').fillna(0)

    if user_id not in user_movie_matrix.index:
        return []

    # Масштабируем рейтинги для корректного расчёта сходства
    scaler = MinMaxScaler()
    user_movie_scaled = pd.DataFrame(
        scaler.fit_transform(user_movie_matrix),
        index=user_movie_matrix.index,
        columns=user_movie_matrix.columns
    )

    # Косинусное сходство между всеми пользователями
    similarity_matrix = cosine_similarity(user_movie_scaled)
    similarity_df = pd.DataFrame(similarity_matrix, index=user_movie_matrix.index, columns=user_movie_matrix.index)

    # Берём только похожих пользователей с порогом
    similar_users = similarity_df.loc[user_id]
    similar_users = similar_users[similar_users >= similarity_threshold]
    similar_users = similar_users.drop(user_id, errors='ignore')

    if similar_users.empty:
        return []

    # Фильмы, которые пользователь уже оценил
    seen_movies = user_movie_matrix.loc[user_id][user_movie_matrix.loc[user_id] > 0].index

    # Взвешиваем рейтинги похожих пользователей
    weighted_ratings = user_movie_matrix.loc[similar_users.index].T.dot(similar_users)
    sum_of_weights = similar_users.sum()
    predicted_scores = weighted_ratings / sum_of_weights

    # Убираем уже оценённые фильмы
    predicted_scores = predicted_scores.drop(index=seen_movies, errors='ignore')

    # Сортируем и берём топ-N рекомендаций
    top_recommendations = predicted_scores.sort_values(ascending=False).head(top_n).index.tolist()

    return top_recommendations
