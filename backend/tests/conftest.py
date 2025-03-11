import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from main import app
from app.db.database import Base
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.event_repository import EventRepository
from app.db.repositories.checkin_repository import CheckInRepository
from app.db.models.user import User, UserCreate
from app.db.models.event import Event
from app.db.models.checkin import CheckIn

# Test database settings
TEST_DATABASE_URL = settings.DATABASE_URL.replace(settings.DATABASE_NAME, f"test_{settings.DATABASE_NAME}")

# Test client
@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

# Database fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def test_db(test_engine):
    """Create a test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()

# Repository fixtures
@pytest.fixture
async def user_repository(test_db):
    """User repository fixture."""
    return UserRepository(test_db)

@pytest.fixture
async def event_repository(test_db):
    """Event repository fixture."""
    return EventRepository(test_db)

@pytest.fixture
async def checkin_repository(test_db):
    """Check-in repository fixture."""
    return CheckInRepository(test_db)

# Test data fixtures
@pytest.fixture
async def test_user(user_repository):
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password="hashed_password",
        current_streak=0,
        longest_streak=0,
        total_checkins=0,
        achievements=[]
    )
    created_user = await user_repository.create(user)
    return created_user

@pytest.fixture
async def test_event(event_repository, test_user):
    """Create a test event."""
    event = Event(
        title="Test Event",
        description="A test event for testing",
        creator_id=test_user.id,
        is_public=True
    )
    created_event = await event_repository.create(event)
    return created_event

@pytest.fixture
async def test_checkin(checkin_repository, test_user, test_event):
    """Create a test check-in."""
    checkin = CheckIn(
        user_id=test_user.id,
        event_id=test_event.id,
        check_date=datetime.utcnow(),
        streak_count=1
    )
    created_checkin = await checkin_repository.create(checkin)
    return created_checkin