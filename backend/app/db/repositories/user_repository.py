from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.db.models.user import User
from app.core.exceptions import NotFoundException

class UserRepository:
    """Repository for User model database operations.
    
    This class handles all database interactions for the User model.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID.
        
        Args:
            user_id: The ID of the user to retrieve.
            
        Returns:
            The user if found, None otherwise.
        """
        if not ObjectId.is_valid(user_id):
            return None
            
        user_data = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(**user_data)
        return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email.
        
        Args:
            email: The email of the user to retrieve.
            
        Returns:
            The user if found, None otherwise.
        """
        user_data = await self.collection.find_one({"email": email})
        if user_data:
            return User(**user_data)
        return None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username.
        
        Args:
            username: The username of the user to retrieve.
            
        Returns:
            The user if found, None otherwise.
        """
        user_data = await self.collection.find_one({"username": username})
        if user_data:
            return User(**user_data)
        return None
    
    async def create(self, user: User) -> User:
        """Create a new user.
        
        Args:
            user: The user to create.
            
        Returns:
            The created user with ID.
        """
        user_dict = user.dict(exclude={"id"})
        result = await self.collection.insert_one(user_dict)
        user.id = result.inserted_id
        return user
    
    async def update(self, user_id: str, update_data: dict) -> User:
        """Update a user.
        
        Args:
            user_id: The ID of the user to update.
            update_data: The data to update.
            
        Returns:
            The updated user.
            
        Raises:
            NotFoundException: If the user is not found.
        """
        if not ObjectId.is_valid(user_id):
            raise NotFoundException(detail=f"Invalid user ID: {user_id}")
            
        # Add updated_at timestamp
        update_data["updated_at"] = User.updated_at.default_factory()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
            
        return await self.get_by_id(user_id)
    
    async def delete(self, user_id: str) -> bool:
        """Delete a user.
        
        Args:
            user_id: The ID of the user to delete.
            
        Returns:
            True if the user was deleted, False otherwise.
        """
        if not ObjectId.is_valid(user_id):
            return False
            
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination.
        
        Args:
            skip: Number of users to skip.
            limit: Maximum number of users to return.
            
        Returns:
            List of users.
        """
        cursor = self.collection.find().skip(skip).limit(limit)
        users = [User(**user) async for user in cursor]
        return users
    
    async def get_leaderboard(self, limit: int = 10) -> List[User]:
        """Get users sorted by longest streak.
        
        Args:
            limit: Maximum number of users to return.
            
        Returns:
            List of users sorted by longest streak.
        """
        cursor = self.collection.find().sort("longest_streak", -1).limit(limit)
        users = [User(**user) async for user in cursor]
        return users
    
    async def update_streak(self, user_id: str, current_streak: int, longest_streak: int) -> User:
        """Update a user's streak information.
        
        Args:
            user_id: The ID of the user to update.
            current_streak: The current streak count.
            longest_streak: The longest streak count.
            
        Returns:
            The updated user.
            
        Raises:
            NotFoundException: If the user is not found.
        """
        update_data = {
            "current_streak": current_streak,
            "longest_streak": max(longest_streak, current_streak),
            "updated_at": User.updated_at.default_factory()
        }
        
        return await self.update(user_id, update_data)
    
    async def add_achievement(self, user_id: str, achievement: str) -> User:
        """Add an achievement to a user.
        
        Args:
            user_id: The ID of the user to update.
            achievement: The achievement to add.
            
        Returns:
            The updated user.
            
        Raises:
            NotFoundException: If the user is not found.
        """
        if not ObjectId.is_valid(user_id):
            raise NotFoundException(detail=f"Invalid user ID: {user_id}")
            
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$addToSet": {"achievements": achievement},
                "$set": {"updated_at": User.updated_at.default_factory()}
            }
        )
        
        if result.matched_count == 0:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
            
        return await self.get_by_id(user_id)
    
    async def increment_checkin_count(self, user_id: str) -> User:
        """Increment a user's total check-in count.
        
        Args:
            user_id: The ID of the user to update.
            
        Returns:
            The updated user.
            
        Raises:
            NotFoundException: If the user is not found.
        """
        if not ObjectId.is_valid(user_id):
            raise NotFoundException(detail=f"Invalid user ID: {user_id}")
            
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$inc": {"total_checkins": 1},
                "$set": {"updated_at": User.updated_at.default_factory()}
            }
        )
        
        if result.matched_count == 0:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
            
        return await self.get_by_id(user_id)