from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Separate async engine for Celery worker
_worker_engine = create_async_engine(
    settings.DATABASE_URL,
    # NullPool avoids reusing connections across
    # task executions/forked worker processes
    poolclass=NullPool,
)

WorkerSessionLocal = async_sessionmaker(
    bind=_worker_engine,
    expire_on_commit=False,
)
