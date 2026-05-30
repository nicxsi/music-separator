from logging.config import fileConfig

from alembic import context
from app.core.config import settings
from app.infrastructure.database.engine import engine
from app.infrastructure.database.models.job_model import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# metadata from ORM
target_metadata = Base.metadata


def run_migrations_offline():
    url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

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
