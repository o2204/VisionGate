from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from urllib.parse import unquote

from src.core.config import settings


class Base(DeclarativeBase):
    pass

database_url = unquote(settings.DATABASE_URL)

engine: AsyncEngine = create_async_engine(
    database_url,
    echo=False,  # set True only for debugging
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()