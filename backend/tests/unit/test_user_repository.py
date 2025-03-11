import pytest
from bson import ObjectId
from datetime import datetime

from app.db.models.user import User, UserCreate, UserUpdate
from app.core.exceptions import NotFoundException

pytestmark = pytest.mark.asyncio


class TestUserRepository:
    async def test_create_user(self, user_repository):
        # Arrange
        user = User(
            email="newuser@example.com",
            username="newuser",
            name="New User",
            current_streak=0,
            longest_streak=0,
            total_checkins=0,
            achievements=[]
        )
        
        # Act
        created_user = await user_repository.create(user)
        
        # Assert
        assert created_user.id is not None
        assert created_user.email == "newuser@example.com"
        assert created_user.username == "newuser"
        assert created_user.name == "New User"
        assert created_user.created_at is not None
        assert created_user.updated_at is not None
    
    async def test_get_by_id(self, user_repository, test_user):
        # Act
        retrieved_user = await user_repository.get_by_id(str(test_user.id))
        
        # Assert
        assert retrieved_user is not None
        assert str(retrieved_user.id) == str(test_user.id)
        assert retrieved_user.email == test_user.email
    
    async def test_get_by_id_not_found(self, user_repository):
        # Act
        non_existent_id = str(ObjectId())
        retrieved_user = await user_repository.get_by_id(non_existent_id)
        
        # Assert
        assert retrieved_user is None
    
    async def test_get_by_email(self, user_repository, test_user):
        # Act
        retrieved_user = await user_repository.get_by_email(test_user.email)
        
        # Assert
        assert retrieved_user is not None
        assert str(retrieved_user.id) == str(test_user.id)
        assert retrieved_user.email == test_user.email
    
    async def test_get_by_email_not_found(self, user_repository):
        # Act
        retrieved_user = await user_repository.get_by_email("nonexistent@example.com")
        
        # Assert
        assert retrieved_user is None
    
    async def test_get_by_username(self, user_repository, test_user):
        # Act
        retrieved_user = await user_repository.get_by_username(test_user.username)
        
        # Assert
        assert retrieved_user is not None
        assert str(retrieved_user.id) == str(test_user.id)
        assert retrieved_user.username == test_user.username
    
    async def test_get_by_username_not_found(self, user_repository):
        # Act
        retrieved_user = await user_repository.get_by_username("nonexistentuser")
        
        # Assert
        assert retrieved_user is None
    
    async def test_get_all(self, user_repository, test_user):
        # Act
        users = await user_repository.get_all()
        
        # Assert
        assert len(users) >= 1
        assert any(str(user.id) == str(test_user.id) for user in users)
    
    async def test_update(self, user_repository, test_user):
        # Arrange
        update_data = {"name": "Updated Name", "bio": "New bio"}
        
        # Act
        updated_user = await user_repository.update(str(test_user.id), update_data)
        
        # Assert
        assert updated_user.name == "Updated Name"
        assert updated_user.bio == "New bio"
        assert updated_user.updated_at > test_user.updated_at
    
    async def test_update_not_found(self, user_repository):
        # Arrange
        non_existent_id = str(ObjectId())
        update_data = {"name": "Updated Name"}
        
        # Act & Assert
        with pytest.raises(NotFoundException):
            await user_repository.update(non_existent_id, update_data)
    
    async def test_delete(self, user_repository, test_user):
        # Act
        result = await user_repository.delete(str(test_user.id))
        
        # Assert
        assert result is True
        deleted_user = await user_repository.get_by_id(str(test_user.id))
        assert deleted_user is None
    
    async def test_delete_not_found(self, user_repository):
        # Act
        non_existent_id = str(ObjectId())
        result = await user_repository.delete(non_existent_id)
        
        # Assert
        assert result is False
    
    async def test_get_leaderboard(self, user_repository, test_user):
        # Arrange
        # Update test_user to have a streak
        await user_repository.update(str(test_user.id), {"longest_streak": 5})
        
        # Create another user with a different streak
        user2 = User(
            email="user2@example.com",
            username="user2",
            name="User Two",
            current_streak=3,
            longest_streak=10,
            total_checkins=15,
            achievements=[]
        )
        await user_repository.create(user2)
        
        # Act
        leaderboard = await user_repository.get_leaderboard(limit=5)
        
        # Assert
        assert len(leaderboard) >= 2
        # Check that the leaderboard is sorted by longest_streak in descending order
        assert leaderboard[0].longest_streak >= leaderboard[1].longest_streak
    
    async def test_update_streak(self, user_repository, test_user):
        # Act
        updated_user = await user_repository.update_streak(
            str(test_user.id), current_streak=7, longest_streak=7
        )
        
        # Assert
        assert updated_user.current_streak == 7
        assert updated_user.longest_streak == 7
        assert updated_user.updated_at > test_user.updated_at
    
    async def test_update_streak_not_found(self, user_repository):
        # Act & Assert
        non_existent_id = str(ObjectId())
        with pytest.raises(NotFoundException):
            await user_repository.update_streak(non_existent_id, 5, 5)
    
    async def test_increment_checkins(self, user_repository, test_user):
        # Arrange
        initial_checkins = test_user.total_checkins
        
        # Act
        updated_user = await user_repository.increment_checkins(str(test_user.id))
        
        # Assert
        assert updated_user.total_checkins == initial_checkins + 1
        assert updated_user.updated_at > test_user.updated_at
    
    async def test_increment_checkins_not_found(self, user_repository):
        # Act & Assert
        non_existent_id = str(ObjectId())
        with pytest.raises(NotFoundException):
            await user_repository.increment_checkins(non_existent_id)
    
    async def test_add_achievement(self, user_repository, test_user):
        # Act
        updated_user = await user_repository.add_achievement(
            str(test_user.id), achievement="First Check-in"
        )
        
        # Assert
        assert "First Check-in" in updated_user.achievements
        assert updated_user.updated_at > test_user.updated_at
        
        # Test adding the same achievement again (should not duplicate)
        updated_user2 = await user_repository.add_achievement(
            str(test_user.id), achievement="First Check-in"
        )
        assert updated_user2.achievements.count("First Check-in") == 1
    
    async def test_add_achievement_not_found(self, user_repository):
        # Act & Assert
        non_existent_id = str(ObjectId())
        with pytest.raises(NotFoundException):
            await user_repository.add_achievement(non_existent_id, "Achievement")