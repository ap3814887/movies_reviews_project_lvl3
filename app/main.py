from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router
from .database import Base, engine

from .sentiment import classify_sentiment
app = FastAPI(title="Movie Reviews API")

# Добавление CORS middleware (разрешаем доступ к API со всех доменов)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Разрешить запросы с любых доменов 
    allow_credentials=True,         # Разрешить использование cookie и авторизационных заголовков
    allow_methods=["*"],            # Разрешить все HTTP-методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],            # Разрешить любые заголовки в запросах
)

# Подключение всех маршрутов (эндпоинтов) из файла routes.py
app.include_router(router)

# Создаём таблицы при первом запуске
Base.metadata.create_all(bind=engine)
