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
