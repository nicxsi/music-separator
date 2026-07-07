from sqlalchemy.ext.asyncio import async_sessionmaker

from app.infrastructure.database.engine import engine

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
