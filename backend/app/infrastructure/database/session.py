from app.infrastructure.database.engine import engine
from sqlalchemy.ext.asyncio import async_sessionmaker

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
