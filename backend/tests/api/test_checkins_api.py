import pytest
from fastapi.testclient import TestClient
from bson import ObjectId
from datetime import datetime, timedelta

from main import app

# Initialize test client
client = TestClient(app)


@pytest.fixture
def test_user_data():
    """Test user data for creating a new user."""
    return {
        "email": "checkintest@example.com",
        "username": "checkintestuser",
        "name": "Check-in Test User"
    }


@pytest.fixture
def created_test_user(test_user_data):
    """Create a test user and return the response data."""
    response = client.post("/api/v1/users/", json=test_user_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def test_event_data():
    """Test event data for creating a new event."""
    return {
        "name": "Check-in Test Event",
        "description": "An event for testing check-ins",
        "is_public": True,
        "frequency": "daily"
    }


@pytest.fixture
def created_test_event(created_test_user, test_event_data):
    """Create a test event and return the response data."""
    response = client.post(
        "/api/v1/events/", 
        json=test_event_data,
        params={"current_user_id": created_test_user["id"]}
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def test_checkin_data():
    """Test check-in data for creating a new check-in."""
    return {
        "note": "Test check-in note",
        "mood": "happy"
    }


@pytest.fixture
def created_test_checkin(created_test_user, created_test_event, test_checkin_data):
    """Create a test check-in and return the response data."""
    checkin_data = {
        **test_checkin_data,
        "event_id": created_test_event["id"]
    }
    response = client.post(
        "/api/v1/checkins/", 
        json=checkin_data,
        params={"current_user_id": created_test_user["id"]}
    )
    assert response.status_code == 201
    return response.json()


def test_create_checkin(created_test_user, created_test_event, test_checkin_data):
    """Test creating a new check-in."""
    checkin_data = {
        **test_checkin_data,
        "event_id": created_test_event["id"]
    }
    response = client.post(
        "/api/v1/checkins/", 
        json=checkin_data,
        params={"current_user_id": created_test_user["id"]}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["note"] == test_checkin_data["note"]
    assert data["mood"] == test_checkin_data["mood"]
    assert data["user_id"] == created_test_user["id"]
    assert data["event_id"] == created_test_event["id"]
    assert "id" in data
    assert "created_at" in data
    assert "check_date" in data


def test_create_checkin_duplicate_today(created_test_user, created_test_event, created_test_checkin):
    """Test creating a duplicate check-in for the same event on the same day."""
    checkin_data = {
        "note": "Duplicate check-in",
        "mood": "excited",
        "event_id": created_test_event["id"]
    }
    response = client.post(
        "/api/v1/checkins/", 
        json=checkin_data,
        params={"current_user_id": created_test_user["id"]}
    )
    assert response.status_code == 400
    assert "You have already checked in to this event today" in response.json()["detail"]


def test_get_checkins(created_test_checkin):
    """Test getting all check-ins."""
    response = client.get("/api/v1/checkins/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Check if our created test check-in is in the list
    assert any(checkin["id"] == created_test_checkin["id"] for checkin in data)


def test_get_checkins_by_user(created_test_user, created_test_checkin):
    """Test getting check-ins filtered by user ID."""
    response = client.get(
        "/api/v1/checkins/",
        params={"user_id": created_test_user["id"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # All check-ins should belong to the specified user
    assert all(checkin["user_id"] == created_test_user["id"] for checkin in data)
    # Check if our created test check-in is in the list
    assert any(checkin["id"] == created_test_checkin["id"] for checkin in data)


def test_get_checkin_by_id(created_test_checkin):
    """Test getting a specific check-in by ID."""
    response = client.get(f"/api/v1/checkins/{created_test_checkin['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_test_checkin["id"]
    assert data["note"] == created_test_checkin["note"]
    assert data["mood"] == created_test_checkin["mood"]


def test_get_checkin_not_found():
    """Test getting a check-in that doesn't exist."""
    non_existent_id = str(ObjectId())
    response = client.get(f"/api/v1/checkins/{non_existent_id}")
    assert response.status_code == 404
    assert f"Check-in with ID {non_existent_id} not found" in response.json()["detail"]


def test_get_latest_checkin(created_test_user, created_test_checkin):
    """Test getting the latest check-in for a user."""
    response = client.get(f"/api/v1/checkins/user/{created_test_user['id']}/latest")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == created_test_user["id"]
    # The latest check-in should be our created test check-in
    assert data["id"] == created_test_checkin["id"]


def test_get_latest_checkin_not_found():
    """Test getting the latest check-in for a user with no check-ins."""
    # Create a new user with no check-ins
    new_user_data = {
        "email": "nocheckinsuser@example.com",
        "username": "nocheckinsuser",
        "name": "No Check-ins User"
    }
    new_user_response = client.post("/api/v1/users/", json=new_user_data)
    new_user = new_user_response.json()
    
    response = client.get(f"/api/v1/checkins/user/{new_user['id']}/latest")
    assert response.status_code == 404
    assert f"No check-ins found for user with ID {new_user['id']}" in response.json()["detail"]


def test_get_user_event_streak(created_test_user, created_test_event, created_test_checkin):
    """Test getting the streak for a user-event pair."""
    response = client.get(
        f"/api/v1/checkins/user/{created_test_user['id']}/event/{created_test_event['id']}/streak"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == created_test_user["id"]
    assert data["event_id"] == created_test_event["id"]
    assert "current_streak" in data
    assert "longest_streak" in data


def test_get_user_streaks(created_test_user, created_test_checkin):
    """Test getting all streaks for a user."""
    response = client.get(f"/api/v1/checkins/user/{created_test_user['id']}/streaks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # All streaks should belong to the specified user
    assert all(streak["user_id"] == created_test_user["id"] for streak in data)


def test_get_event_leaderboard(created_test_event, created_test_checkin):
    """Test getting the leaderboard for an event."""
    response = client.get(f"/api/v1/checkins/event/{created_test_event['id']}/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # The leaderboard should include our test user
    assert any(entry["event_id"] == created_test_event["id"] for entry in data)