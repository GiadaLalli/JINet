"""Database support."""

from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker

from jinet.config import settings

engine = AsyncEngine(create_engine(settings.database_uri, future=True, echo=True))


async def database_session() -> AsyncSession:
    """Dependency for a database session."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
