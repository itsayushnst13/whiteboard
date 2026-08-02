"""DATABASE_URL normalization for SQLAlchemy's asyncpg driver.

Managed Postgres providers (Neon, Supabase, old-style Heroku, ...) hand
out `postgres://` or `postgresql://` connection strings with libpq-style
query parameters — most importantly `sslmode=require`, which Neon always
includes.

SQLAlchemy's asyncpg dialect does two things that make a raw provider URL
unsafe to use as-is:

1. It needs the `+asyncpg` driver suffix on the scheme; a bare
   `postgresql://` URL resolves to psycopg2, which isn't installed here.
2. Its `create_connect_args` passes every URL query parameter straight
   through as a keyword argument to `asyncpg.connect()` — it does not
   parse them as a libpq DSN. `asyncpg.connect()` has no `sslmode`
   parameter (only `ssl`), so `?sslmode=require` crashes with
   `TypeError: connect() got an unexpected keyword argument 'sslmode'`.
   (Verified directly against installed asyncpg 0.30: passing
   `sslmode="require"` raises that TypeError, while `ssl=True` does not.)

`prepare_database_url` strips the libpq-only params out of the URL and
returns the equivalent `connect_args` for `create_async_engine` (and
Alembic's engine) to pass instead, so both the app and migrations connect
to Neon (or any sslmode-bearing provider) correctly.
"""

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def prepare_database_url(raw_url: str) -> tuple[str, dict[str, object]]:
    parts = urlsplit(raw_url)

    # Only Postgres URLs need any of this. Bail out early for anything else
    # (notably SQLite, used by the test suite and handy for local dev):
    # a urlsplit/urlunsplit round-trip is *lossy* when netloc is empty,
    # which is exactly SQLite's shape — "sqlite+aiosqlite:////tmp/x.db"
    # would come back as "sqlite+aiosqlite://tmp/x.db" and fail to open.
    if parts.scheme.split("+", 1)[0] not in ("postgres", "postgresql"):
        return raw_url, {}

    scheme = parts.scheme
    if scheme in ("postgres", "postgresql"):
        scheme = "postgresql+asyncpg"

    query = dict(parse_qsl(parts.query))
    sslmode = query.pop("sslmode", None)
    # Neon also appends `channel_binding=require`, another libpq-only
    # param asyncpg doesn't understand; drop it too. `ssl` is dropped and
    # re-added below (as a real bool) rather than trusted verbatim, since
    # a stray `ssl=require`/`ssl=true` string from the provider would hit
    # the same "not a kwarg asyncpg expects a bare bool/SSLContext for"
    # problem.
    query.pop("ssl", None)
    query.pop("channel_binding", None)

    clean_url = urlunsplit((scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))

    connect_args: dict[str, object] = {}
    if sslmode and sslmode != "disable":
        connect_args["ssl"] = True

    return clean_url, connect_args
