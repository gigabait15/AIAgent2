from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    """
    Класс конфигурации приложения, получающий значения из переменных окружения.

    Используется библиотека `pydantic-settings`, которая автоматически загружает переменные
    из указанного `.env` файла.
    Атрибуты:
        SID (str): ID сервиса twillo
        TOKEN (str): токен доступа сервиса twillo
        OPENAI (str): API key openai

    """
    SID: str
    TOKEN: str
    OPENAI: str

    class Config:
        env_file = '.env'
        case_sensitive = True