from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_TITLE: str = "Team Finder API"
    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ACCESS_COOKIE_NAME: str = "__sid"
    REFRESH_COOKIE_NAME: str = "__rid"
    COOKIE_ENCRYPTION_KEY: str
    COOKIE_MAX_AGE_ACCESS: int = 30 * 60
    COOKIE_MAX_AGE_REFRESH: int = 7 * 24 * 60 * 60

    PARSER_URL: str = "http://parser:8001"
    REDIS_URL: str = "redis://redis:6379/0"

    class Config:
        env_file = Path(__file__).resolve().parent.parent / ".env"
    

settings = Settings()
