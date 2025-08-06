#from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from sqlalchemy import URL, create_engine, text
from .config import settings

# Создание синхронного движка подключения к базе данных PostgreSQL
# Строка подключения берётся из .env через config.py (через settings.DATABASE_URL_psycopg2)
engine = create_engine(
    url=settings.DATABASE_URL_psycopg2,
    echo=False
)

# Создание фабрики сессий
# autocommit=False — изменения сохраняются только после явного вызова commit()
# autoflush=False — SQLAlchemy не будет автоматически сбрасывать изменения в БД перед каждым запросом
# bind=engine — указываем, какой движок использовать
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Базовый класс для всех моделей (через declarative mapping API)
# От него наследуются все таблицы (модели)
Base = declarative_base()


def get_db():
    """
    Функция для получения сессии базы данных.
    Используется в FastAPI для внедрения зависимости (Depends).

    Автоматически управляет временем жизни сессии — открывает её,
    а затем закрывает после завершения работы.
    """
    with SessionLocal() as db: # Контекстный менеджер автоматически закрывает сессию после выхода из блока
        yield db # Генератор — возвращает активную сессию, используется в эндпоинтах
