"""Database support."""

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

from jinet.config import settings

engine = create_async_engine(str(settings.database_uri), future=True, echo=True)


async def database_session() -> AsyncSession:
    """Dependency for a database session."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
