from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from environment variables and backend/.env.

    Real environment variables take precedence over values in .env.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # e.g. postgresql+psycopg://user:password@localhost:5432/rewind
    # Special characters in the password must be URL-encoded ("@" -> "%40").
    DATABASE_URL: str


@lru_cache
def get_settings() -> Settings:
    # Cached so .env is parsed once; tests can call get_settings.cache_clear().
    return Settings()


settings = get_settings()
