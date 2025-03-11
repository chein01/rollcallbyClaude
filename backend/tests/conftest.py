import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.testclient import TestClient
from bson import ObjectId
from datetime import datetime, timedelta

from app.core.config import settings
from main import app
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.event_repository import EventRepository
from app.db.repositories.checkin_repository import CheckInRepository
from app.db.models.user import User, UserCreate
from app.db.models.event import Event
from app.db.models.checkin import CheckIn

# Test database settings
TEST_MONGODB_URL = settings.MONGODB_URL
TEST_DATABASE_NAME = "test_rollcall"

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
async def mongodb_client():
    """MongoDB client fixture."""
    client = AsyncIOMotorClient(TEST_MONGODB_URL)
    yield client
    client.close()

@pytest.fixture(scope="function")
async def mongodb(mongodb_client):
    """MongoDB test database fixture."""
    db = mongodb_client[TEST_DATABASE_NAME]
    yield db
    # Clean up after test
    await mongodb_client.drop_database(TEST_DATABASE_NAME)

# Repository fixtures
@pytest.fixture
async def user_repository(mongodb):
    """User repository fixture."""
    return UserRepository(mongodb)

@pytest.fixture
async def event_repository(mongodb):
    """Event repository fixture."""
    return EventRepository(mongodb)

@pytest.fixture
async def checkin_repository(mongodb):
    """Check-in repository fixture."""
    return CheckInRepository(mongodb)

# Test data fixtures
@pytest.fixture
async def test_user(user_repository):
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        name="Test User",
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
        name="Test Event",
        description="A test event for testing",
        creator_id=test_user.id,
        participants=[test_user.id],
        is_public=True,
        frequency="daily"
    )
    created_event = await event_repository.create(event)
    return created_event

@pytest.fixture
async def test_checkin(checkin_repository, test_user, test_event):
    """Create a test check-in."""
    checkin = CheckIn(
        user_id=test_user.id,
        event_id=test_event.id,
        note="Test check-in",
        mood="happy"
    )
    created_checkin = await checkin_repository.create(checkin)
    return created_checkin