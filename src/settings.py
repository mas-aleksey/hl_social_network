from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URI: str
    SECRET_KEY: str | None = None


def get_settings():
    return Settings()
