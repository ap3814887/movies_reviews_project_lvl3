from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import torch
from .sentiment_types import SentimentEnum

# Более точная и сбалансированная модель для анализа тональности на русском
MODEL_NAME = "cointegrated/rubert-tiny-sentiment-balanced"

# Загружаем токенизатор и модель
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# Метки классов строго соответствуют выходу модели
labels = ['negative', 'neutral', 'positive']

def classify_sentiment(text: str) -> SentimentEnum:
    # Токенизация входного текста
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    # Вычисление предсказания без вычисления градиентов
    with torch.no_grad():
        logits = model(**inputs).logits

    # Преобразование логитов в вероятности
    probs = softmax(logits.numpy()[0])
    predicted_index = probs.argmax()
    predicted_label = labels[predicted_index]

    return SentimentEnum(predicted_label)