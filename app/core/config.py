import secrets
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    PROJECT_NAME: str
    DESCRIPTION: str
    VERSION: str

    SECRET_KEY: str = secrets.token_urlsafe(32)
    BASE_DIR: Path = Path(__file__).parent.parent

    API_STR: str = "/api/v"

    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = ENVIRONMENT != "production"

    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    FOOTBALL_DATA_API_KEY: str

    ADMIN_PASSWORD: bytes

    @computed_field  # type: ignore
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
