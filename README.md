UPD: Добавлена сущность users, авторизация и ограничение доступа по JWT-токену, реализована рекомендательная логика на бэкенде (4 новых маршрута с разными методами для рекомендаций).
Установка и запуск проекта:

Требования:
Версия Python 3.10+

1)Клонировать репозиторий и активировать окружение

git clone https://github.com/your-username/movie-reviews.git
cd movie_reviews
python -m venv venv
venv\Scripts\activate

2)Установить зависимости

pip install -r requirements.txt

3)Настроить подключение к БД

DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=movies_reviews_db

4)Создать БД (если не создана)

В PostgreSQL:
CREATE DATABASE movies_reviews_db;


5)Применить миграции Alembic (последняя версия: 08e315164bfa_.py)

alembic upgrade head

6)Запустить приложение

uvicorn app.main:app --reload
