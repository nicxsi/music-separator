from logging.config import fileConfig

from sqlalchemy.engine import make_url

from alembic import context
from app.core.config import settings
from app.infrastructure.database.base import Base
from app.infrastructure.database.engine import engine
from app.infrastructure.database.models import (  # noqa: F401
    browser_session_model,
    job_model,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# metadata from ORM
target_metadata = Base.metadata


def run_migrations_offline():
    url = make_url(settings.DATABASE_URL).set(drivername="postgresql")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
