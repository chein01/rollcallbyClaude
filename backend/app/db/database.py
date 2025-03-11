from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.core.config import settings

# Create async engine for MySQL
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# Create sync engine for testing and utilities
sync_engine = create_engine(
    settings.DATABASE_URL.replace("mysql+aiomysql", "mysql+pymysql"),
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# Session factories
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

# Base class for all models
Base = declarative_base()


# Dependency to get DB session
async def get_db():
    """Dependency for getting async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Initialize database tables
def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=sync_engine)