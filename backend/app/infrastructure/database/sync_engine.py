"""
The initialization module for the SQLAlchemy synchronous engine and
the session factory

It is used exclusively in synchronous application contexts,
mainly inside Celery workers. Since the main environment
variable DATABASE_URL is configured for the asynchronous driver (asyncpg)
for FastAPI, this module dynamically adapts it
to the synchronous driver (psycopg2)
"""

from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# asyncpg is only for FastAPI (async). Celery-worker works
# in the context of synchronization, so use psycopg2.
_sync_url = settings.DATABASE_URL.replace(
    "postgresql+asyncpg://", "postgresql+psycopg2://"
)

# pool_pre_ping=True — critically important for the worker.
# Before each request from the pool, the engine checks (makes a "ping")
# whether the session with PostgreSQL is alive.
# This prevents OperationalError tasks from crashing
# if the database has rebooted or an idle connection has been terminated
# for a long time.
sync_engine = create_engine(_sync_url, pool_pre_ping=True)

# Synchronous session factory for the context manager
# `with SyncSessionLocal() as session:`
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)
