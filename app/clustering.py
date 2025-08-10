import re
from collections import defaultdict
from functools import lru_cache

import pymorphy2
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Скачиваем стоп-слова один раз
nltk.download('stopwords')
from nltk.corpus import stopwords

# Инициализация морфоанализатора и стоп-слов
morph = pymorphy2.MorphAnalyzer()
stop_words = set(stopwords.words('russian'))

# Регулярка для токенизации русских слов
WORD_RE = re.compile(r'[а-яё]+', re.IGNORECASE)

@lru_cache(maxsize=100_000)
def lemmatize_word(word: str) -> str:
    """Лемматизация с кешированием."""
    return morph.parse(word)[0].normal_form

def preprocess_text(text: str) -> str:
    """Токенизация, лемматизация и удаление стоп-слов."""
    words = WORD_RE.findall(text.lower())
    lemmas = [lemmatize_word(w) for w in words]
    filtered = [lemma for lemma in lemmas if lemma not in stop_words]
    return ' '.join(filtered)

def cluster_movies_by_reviews(db, num_clusters: int = 5) -> dict[int, list[str]]:
    """Кластеризация фильмов по тематике отзывов."""
    from app.models import Review, Movie

    # Загружаем все отзывы
    reviews = db.query(Review).all()
    if not reviews:
        return {}

    # Группируем отзывы по movie_id с предобработкой
    reviews_by_movie = defaultdict(list)
    for review in reviews:
        reviews_by_movie[review.movie_id].append(preprocess_text(review.review_text))

    # Формируем список документов для кластеризации
    movie_ids = list(reviews_by_movie.keys())
    processed_reviews = [" ".join(texts) for texts in reviews_by_movie.values()]

    if not processed_reviews:
        return {}

    # Векторизация TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(processed_reviews)

    # Кластеризация KMeans
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(tfidf_matrix)

    # Получаем все фильмы за один запрос (чтобы избежать N+1)
    movies = db.query(Movie).filter(Movie.id.in_(movie_ids)).all()
    movie_map = {m.id: m.title for m in movies}

    # Формируем результат: кластер -> список названий фильмов
    result = defaultdict(list)
    for idx, cluster_id in enumerate(clusters):
        movie_title = movie_map.get(movie_ids[idx])
        if movie_title:
            result[int(cluster_id)].append(movie_title)

    return dict(result)
