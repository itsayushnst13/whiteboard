import pytest
from pydantic import ValidationError

from app.config.settings import Environment, Settings


def _settings(**overrides: object) -> Settings:
    defaults = {
        "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/db",
        "REDIS_URL": "redis://localhost:6379/0",
    }
    return Settings(**{**defaults, **overrides})  # type: ignore[arg-type]


def test_cors_origins_parsed_from_comma_separated_string() -> None:
    settings = _settings(BACKEND_CORS_ORIGINS="http://a.com, http://b.com")
    assert settings.BACKEND_CORS_ORIGINS == ["http://a.com", "http://b.com"]


def test_cors_origins_defaults_to_empty_list() -> None:
    assert _settings().BACKEND_CORS_ORIGINS == []


def test_is_production_true_only_in_production_environment() -> None:
    assert _settings(ENVIRONMENT=Environment.PRODUCTION).is_production is True
    assert _settings(ENVIRONMENT=Environment.DEVELOPMENT).is_production is False


def test_is_test_true_only_in_test_environment() -> None:
    assert _settings(ENVIRONMENT=Environment.TEST).is_test is True
    assert _settings(ENVIRONMENT=Environment.PRODUCTION).is_test is False


def test_cors_origins_trailing_slashes_are_stripped() -> None:
    settings = _settings(BACKEND_CORS_ORIGINS="https://app.vercel.app/, https://b.com//")
    assert settings.BACKEND_CORS_ORIGINS == ["https://app.vercel.app", "https://b.com"]


def test_wildcard_cors_rejected_in_production() -> None:
    with pytest.raises(ValidationError):
        _settings(ENVIRONMENT=Environment.PRODUCTION, BACKEND_CORS_ORIGINS="*")
    # Still allowed outside production for local convenience.
    assert _settings(BACKEND_CORS_ORIGINS="*").BACKEND_CORS_ORIGINS == ["*"]
