import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import get_settings
from app.db.url import prepare_database_url
from app.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Every model must be imported (directly or transitively) through
# app.models so it registers on this metadata before autogenerate runs.
target_metadata = Base.metadata

# Same normalization the app's engine uses (app/db/url.py): rewrites
# `postgres(ql)://` to `postgresql+asyncpg://` and strips libpq-only
# query params (sslmode, channel_binding) that asyncpg's connect() would
# otherwise choke on — see that module's docstring for why this matters
# for Neon and similar managed Postgres providers.
_DATABASE_URL, _CONNECT_ARGS = prepare_database_url(get_settings().DATABASE_URL)
config.set_main_option("sqlalchemy.url", _DATABASE_URL)


def run_migrations_offline() -> None:
    """Emit SQL to stdout without a live database connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def _do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations against a live database using the app's async
    engine configuration."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=_CONNECT_ARGS,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(_do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
