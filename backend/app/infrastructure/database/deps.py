from collections.abc import AsyncGenerator

from app.infrastructure.database.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session
