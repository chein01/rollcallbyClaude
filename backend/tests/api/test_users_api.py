import pytest
import uuid
from fastapi.testclient import TestClient

from main import app
from app.db.models.user import User

# Initialize test client
client = TestClient(app)


@pytest.fixture
def test_user_data():
    """Test user data for creating a new user."""
    return {
        "email": "apitest@example.com",
        "username": "apitestuser",
        "name": "API Test User",
        "bio": "A user created for API testing"
    }


@pytest.fixture
def created_test_user(test_user_data):
    """Create a test user and return the response data."""
    response = client.post("/api/v1/users/", json=test_user_data)
    assert response.status_code == 201
    return response.json()


def test_create_user(test_user_data):
    """Test creating a new user."""
    response = client.post("/api/v1/users/", json=test_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["username"] == test_user_data["username"]
    assert data["name"] == test_user_data["name"]
    assert data["bio"] == test_user_data["bio"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["current_streak"] == 0
    assert data["longest_streak"] == 0
    assert data["total_checkins"] == 0
    assert data["achievements"] == []


def test_create_user_duplicate_email(created_test_user, test_user_data):
    """Test creating a user with an email that already exists."""
    response = client.post("/api/v1/users/", json=test_user_data)
    assert response.status_code == 400
    assert "User with this email already exists" in response.json()["detail"]


def test_create_user_duplicate_username(created_test_user):
    """Test creating a user with a username that already exists."""
    new_user_data = {
        "email": "different@example.com",
        "username": created_test_user["username"],  # Same username as existing user
        "name": "Different Name"
    }
    response = client.post("/api/v1/users/", json=new_user_data)
    assert response.status_code == 400
    assert "Username already taken" in response.json()["detail"]


def test_get_users(created_test_user):
    """Test getting all users."""
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Check if our created test user is in the list
    assert any(user["id"] == created_test_user["id"] for user in data)


def test_get_user_by_id(created_test_user):
    """Test getting a specific user by ID."""
    response = client.get(f"/api/v1/users/{created_test_user['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_test_user["id"]
    assert data["email"] == created_test_user["email"]
    assert data["username"] == created_test_user["username"]


def test_get_user_not_found():
    """Test getting a user that doesn't exist."""
    non_existent_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/users/{non_existent_id}")
    assert response.status_code == 404
    assert f"User with ID {non_existent_id} not found" in response.json()["detail"]


def test_update_user(created_test_user):
    """Test updating a user."""
    update_data = {
        "name": "Updated Name",
        "bio": "Updated bio for API testing"
    }
    response = client.put(f"/api/v1/users/{created_test_user['id']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_test_user["id"]
    assert data["name"] == update_data["name"]
    assert data["bio"] == update_data["bio"]
    # Email and username should remain unchanged
    assert data["email"] == created_test_user["email"]
    assert data["username"] == created_test_user["username"]


def test_update_user_not_found():
    """Test updating a user that doesn't exist."""
    non_existent_id = str(uuid.uuid4())
    update_data = {"name": "Updated Name"}
    response = client.put(f"/api/v1/users/{non_existent_id}", json=update_data)
    assert response.status_code == 404


def test_delete_user(created_test_user):
    """Test deleting a user."""
    response = client.delete(f"/api/v1/users/{created_test_user['id']}")
    assert response.status_code == 204
    
    # Verify the user is actually deleted
    get_response = client.get(f"/api/v1/users/{created_test_user['id']}")
    assert get_response.status_code == 404


def test_delete_user_not_found():
    """Test deleting a user that doesn't exist."""
    non_existent_id = str(uuid.uuid4())
    response = client.delete(f"/api/v1/users/{non_existent_id}")
    assert response.status_code == 404
    assert f"User with ID {non_existent_id} not found" in response.json()["detail"]


def test_get_leaderboard(created_test_user):
    """Test getting the user leaderboard."""
    response = client.get("/api/v1/users/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # The created test user should be in the leaderboard
    assert any(user["id"] == created_test_user["id"] for user in data)