"""

config.py - конфигурация подключения к базе данных

"""

from pydantic_settings import BaseSettings, SettingsConfigDict

# Создание класса настроек, который будет автоматически читать переменные окружения
class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str


    # Свойство, которое возвращает URL подключения для SQLAlchemy с драйвером psycopg2
    @property
    def DATABASE_URL_psycopg2(self):
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Значения будут загружаться из файла `.env`
    model_config = SettingsConfigDict(env_file=".env")

# Создание глобального объекта настроек, который можно импортировать и использовать в других частях приложения
settings = Settings()