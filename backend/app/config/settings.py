from enum import StrEnum
from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Typed, validated application configuration sourced from environment
    variables (and a local .env file in development)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    PROJECT_NAME: str = "SyncBoard"
    API_V1_PREFIX: str = "/api/v1"
    VERSION: str = "0.1.0"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # NoDecode: without it, pydantic-settings tries to JSON-decode env/.env
    # values for any list-typed field before our validator below ever runs,
    # so a plain comma-separated string (as documented in .env.example)
    # raises a SettingsError instead of being split.
    BACKEND_CORS_ORIGINS: Annotated[list[str], NoDecode] = Field(default_factory=list)

    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    REDIS_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT is Environment.PRODUCTION

    @property
    def is_test(self) -> bool:
        return self.ENVIRONMENT is Environment.TEST


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor. FastAPI dependencies should call this
    rather than constructing Settings() directly, so the whole app shares
    one validated instance."""
    return Settings()
