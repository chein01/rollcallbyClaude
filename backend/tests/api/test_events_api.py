import pytest
from fastapi.testclient import TestClient
from bson import ObjectId

from main import app

# Initialize test client
client = TestClient(app)


@pytest.fixture
def test_user_data():
    """Test user data for creating a new user."""
    return {
        "email": "eventtest@example.com",
        "username": "eventtestuser",
        "name": "Event Test User"
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
        "name": "Test Event",
        "description": "A test event for API testing",
        "is_public": True,
        "frequency": "daily"
    }


@pytest.fixture
def created_test_event(created_test_user, test_event_data):
    """Create a test event and return the response data."""
    # In a real app, we would need authentication to create an event
    # For testing, we'll mock the current_user_id parameter
    response = client.post(
        "/api/v1/events/", 
        json=test_event_data,
        params={"current_user_id": created_test_user["id"]}
    )
    assert response.status_code == 201
    return response.json()


def test_create_event(created_test_user, test_event_data):
    """Test creating a new event."""
    response = client.post(
        "/api/v1/events/", 
        json=test_event_data,
        params={"current_user_id": created_test_user["id"]}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_event_data["name"]
    assert data["description"] == test_event_data["description"]
    assert data["is_public"] == test_event_data["is_public"]
    assert data["frequency"] == test_event_data["frequency"]
    assert data["creator_id"] == created_test_user["id"]
    assert created_test_user["id"] in data["participants"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_get_events(created_test_event):
    """Test getting all public events."""
    response = client.get("/api/v1/events/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Check if our created test event is in the list
    assert any(event["id"] == created_test_event["id"] for event in data)


def test_get_event_by_id(created_test_event):
    """Test getting a specific event by ID."""
    response = client.get(f"/api/v1/events/{created_test_event['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_test_event["id"]
    assert data["name"] == created_test_event["name"]
    assert data["description"] == created_test_event["description"]


def test_get_event_not_found():
    """Test getting an event that doesn't exist."""
    non_existent_id = str(ObjectId())
    response = client.get(f"/api/v1/events/{non_existent_id}")
    assert response.status_code == 404
    assert f"Event with ID {non_existent_id} not found" in response.json()["detail"]


def test_update_event(created_test_user, created_test_event):
    """Test updating an event."""
    update_data = {
        "name": "Updated Event Name",
        "description": "Updated event description"
    }
    response = client.put(
        f"/api/v1/events/{created_test_event['id']}", 
        json=update_data,
        params={"current_user_id": created_test_user["id"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_test_event["id"]
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    # Other fields should remain unchanged
    assert data["is_public"] == created_test_event["is_public"]
    assert data["frequency"] == created_test_event["frequency"]


def test_update_event_not_creator(created_test_event):
    """Test updating an event by a user who is not the creator."""
    # Create another user who is not the creator
    other_user_data = {
        "email": "other@example.com",
        "username": "otheruser",
        "name": "Other User"
    }
    other_user_response = client.post("/api/v1/users/", json=other_user_data)
    other_user = other_user_response.json()
    
    update_data = {"name": "Unauthorized Update"}
    response = client.put(
        f"/api/v1/events/{created_test_event['id']}", 
        json=update_data,
        params={"current_user_id": other_user["id"]}
    )
    assert response.status_code == 403
    assert "Only the creator can update this event" in response.json()["detail"]


def test_update_event_not_found(created_test_user):
    """Test updating an event that doesn't exist."""
    non_existent_id = str(ObjectId())
    update_data = {"name": "Updated Name"}
    response = client.put(
        f"/api/v1/events/{non_existent_id}", 
        json=update_data,
        params={"current_user_id": created_test_user["id"]}
    )
    assert response.status_code == 404


def test_delete_event(created_test_user, created_test_event):
    """Test deleting an event."""
    response = client.delete(
        f"/api/v1/events/{created_test_event['id']}",
        params={"current_user_id": created_test_user["id"]}
    )
    assert response.status_code == 204
    
    # Verify the event is actually deleted
    get_response = client.get(f"/api/v1/events/{created_test_event['id']}")
    assert get_response.status_code == 404


def test_delete_event_not_creator(created_test_event):
    """Test deleting an event by a user who is not the creator."""
    # Create another user who is not the creator
    other_user_data = {
        "email": "other2@example.com",
        "username": "otheruser2",
        "name": "Other User 2"
    }
    other_user_response = client.post("/api/v1/users/", json=other_user_data)
    other_user = other_user_response.json()
    
    response = client.delete(
        f"/api/v1/events/{created_test_event['id']}",
        params={"current_user_id": other_user["id"]}
    )
    assert response.status_code == 403
    assert "Only the creator can delete this event" in response.json()["detail"]


def test_delete_event_not_found(created_test_user):
    """Test deleting an event that doesn't exist."""
    non_existent_id = str(ObjectId())
    response = client.delete(
        f"/api/v1/events/{non_existent_id}",
        params={"current_user_id": created_test_user["id"]}
    )
    assert response.status_code == 404


def test_join_event(created_test_event):
    """Test joining an event."""
    # Create a new user to join the event
    joiner_data = {
        "email": "joiner@example.com",
        "username": "joineruser",
        "name": "Joiner User"
    }
    joiner_response = client.post("/api/v1/users/", json=joiner_data)
    joiner = joiner_response.json()
    
    response = client.post(
        f"/api/v1/events/{created_test_event['id']}/join",
        params={"current_user_id": joiner["id"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert joiner["id"] in data["participants"]


def test_leave_event(created_test_event):
    """Test leaving an event."""
    # Create a new user to join and then leave the event
    user_data = {
        "email": "leaver@example.com",
        "username": "leaveruser",
        "name": "Leaver User"
    }
    user_response = client.post("/api/v1/users/", json=user_data)
    user = user_response.json()
    
    # First join the event
    join_response = client.post(
        f"/api/v1/events/{created_test_event['id']}/join",
        params={"current_user_id": user["id"]}
    )
    assert join_response.status_code == 200
    
    # Then leave the event
    leave_response = client.post(
        f"/api/v1/events/{created_test_event['id']}/leave",
        params={"current_user_id": user["id"]}
    )
    assert leave_response.status_code == 200
    data = leave_response.json()
    assert user["id"] not in data["participants"]


def test_get_my_events(created_test_user, created_test_event):
    """Test getting events created by the current user."""
    response = client.get(
        "/api/v1/events/my",
        params={"current_user_id": created_test_user["id"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(event["id"] == created_test_event["id"] for event in data)


def test_get_participating_events(created_test_user, created_test_event):
    """Test getting events the user is participating in."""
    response = client.get(
        "/api/v1/events/participating",
        params={"current_user_id": created_test_user["id"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(event["id"] == created_test_event["id"] for event in data)