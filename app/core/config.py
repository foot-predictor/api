import secrets
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    PROJECT_NAME: str
    DESCRIPTION: str
    VERSION: str

    API_STR: str = "/api/v"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = ENVIRONMENT != "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
