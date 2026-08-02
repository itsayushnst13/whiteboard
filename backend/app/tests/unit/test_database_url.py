from app.db.url import prepare_database_url


def test_leaves_local_docker_url_untouched() -> None:
    url, connect_args = prepare_database_url(
        "postgresql+asyncpg://syncboard:syncboard@postgres:5432/syncboard"
    )

    assert url == "postgresql+asyncpg://syncboard:syncboard@postgres:5432/syncboard"
    assert connect_args == {}


def test_rewrites_bare_postgres_scheme_to_asyncpg() -> None:
    url, _ = prepare_database_url("postgres://user:pw@example.com:5432/db")

    assert url.startswith("postgresql+asyncpg://")


def test_rewrites_bare_postgresql_scheme_to_asyncpg() -> None:
    url, _ = prepare_database_url("postgresql://user:pw@example.com:5432/db")

    assert url.startswith("postgresql+asyncpg://")


def test_neon_style_url_gets_ssl_connect_arg_and_no_sslmode_query() -> None:
    url, connect_args = prepare_database_url(
        "postgresql://user:pw@ep-cool-thing-123456.us-east-2.aws.neon.tech/syncboard"
        "?sslmode=require&channel_binding=require"
    )

    assert "sslmode" not in url
    assert "channel_binding" not in url
    assert url.startswith("postgresql+asyncpg://")
    assert connect_args == {"ssl": True}


def test_sslmode_disable_does_not_set_ssl_connect_arg() -> None:
    _, connect_args = prepare_database_url("postgresql://user:pw@example.com/db?sslmode=disable")

    assert connect_args == {}


def test_sqlite_urls_pass_through_untouched() -> None:
    """A urlsplit/urlunsplit round-trip silently mangles URLs with an empty
    netloc, which is exactly SQLite's shape — the absolute-path form below
    would come back with two slashes missing and fail to open. Non-Postgres
    URLs must be returned verbatim."""
    for url in (
        "sqlite+aiosqlite:////tmp/absolute.db",
        "sqlite+aiosqlite:///relative.db",
        "sqlite+aiosqlite:///:memory:",
    ):
        assert prepare_database_url(url) == (url, {})


def test_other_query_params_are_preserved() -> None:
    url, _ = prepare_database_url(
        "postgresql://user:pw@example.com/db?sslmode=require&application_name=syncboard"
    )

    assert "application_name=syncboard" in url
