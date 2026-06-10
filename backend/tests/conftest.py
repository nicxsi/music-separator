import os

import pytest_asyncio
from app.infrastructure.database.models.job_model import Base
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# Explicitly redefining the environment variables for the test environment
# This ensures that the tests will never accidentally connect to a local or
# production database and consume real data
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/music_separator_test"
os.environ["RABBITMQ_URL"] = "amqp://guest:guest@localhost//"

TEST_DATABASE_URL = os.environ["DATABASE_URL"]


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # STEP 1: Create clean tables before running the test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # expire_on_commit=False protects against
    # the DetachedInstanceError error when reading data outside the session
    SessionLocal = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    # STEP 2: Transfer the session to the test
    async with SessionLocal() as session:
        yield session

    # STEP 3: After completing the test, we completely clean the database
    # by deleting the tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()
