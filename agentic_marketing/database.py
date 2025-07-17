"""
Async database setup using SQLAlchemy and asyncpg.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

# Async engine/session for async code
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Sync engine/session for Streamlit UI
sync_engine = create_engine(DATABASE_URL.replace('postgresql+asyncpg', 'postgresql'), echo=True)
SessionLocal = sessionmaker(bind=sync_engine)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
