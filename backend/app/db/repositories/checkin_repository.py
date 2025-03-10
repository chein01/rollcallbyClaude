from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.models.checkin import CheckIn, UserEventStreak
from app.core.exceptions import NotFoundException, BadRequestException

class CheckInRepository:
    """Repository for CheckIn model database operations.
    
    This class handles all database interactions for the CheckIn model.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.checkins
    
    async def get_by_id(self, checkin_id: str) -> Optional[CheckIn]:
        """Get a check-in by ID.
        
        Args:
            checkin_id: The ID of the check-in to retrieve.
            
        Returns:
            The check-in if found, None otherwise.
        """
        if not ObjectId.is_valid(checkin_id):
            return None
            
        checkin_data = await self.collection.find_one({"_id": ObjectId(checkin_id)})
        if checkin_data:
            return CheckIn(**checkin_data)
        return None
    
    async def create(self, checkin: CheckIn) -> CheckIn:
        """Create a new check-in.
        
        Args:
            checkin: The check-in to create.
            
        Returns:
            The created check-in with ID.
        """
        # Calculate streak before saving
        streak_count = await self._calculate_streak(str(checkin.user_id), str(checkin.event_id))
        checkin.streak_count = streak_count
        
        checkin_dict = checkin.dict(exclude={"id"})
        result = await self.collection.insert_one(checkin_dict)
        checkin.id = result.inserted_id
        return checkin
    
    async def update(self, checkin_id: str, update_data: dict) -> CheckIn:
        """Update a check-in.
        
        Args:
            checkin_id: The ID of the check-in to update.
            update_data: The data to update.
            
        Returns:
            The updated check-in.
            
        Raises:
            NotFoundException: If the check-in is not found.
        """
        if not ObjectId.is_valid(checkin_id):
            raise NotFoundException(detail=f"Invalid check-in ID: {checkin_id}")
            
        # Add updated_at timestamp
        update_data["updated_at"] = CheckIn.updated_at.default_factory()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(checkin_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise NotFoundException(detail=f"Check-in with ID {checkin_id} not found")
            
        return await self.get_by_id(checkin_id)
    
    async def delete(self, checkin_id: str) -> bool:
        """Delete a check-in.
        
        Args:
            checkin_id: The ID of the check-in to delete.
            
        Returns:
            True if the check-in was deleted, False otherwise.
        """
        if not ObjectId.is_valid(checkin_id):
            return False
            
        result = await self.collection.delete_one({"_id": ObjectId(checkin_id)})
        return result.deleted_count > 0
    
    async def get_by_user_and_event(self, user_id: str, event_id: str, skip: int = 0, limit: int = 100) -> List[CheckIn]:
        """Get check-ins for a specific user and event.
        
        Args:
            user_id: The ID of the user.
            event_id: The ID of the event.
            skip: Number of check-ins to skip.
            limit: Maximum number of check-ins to return.
            
        Returns:
            List of check-ins for the user and event.
        """
        if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(event_id):
            return []
            
        cursor = self.collection.find({
            "user_id": ObjectId(user_id),
            "event_id": ObjectId(event_id)
        }).sort("check_date", -1).skip(skip).limit(limit)
        
        checkins = [CheckIn(**checkin) async for checkin in cursor]
        return checkins
    
    async def get_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[CheckIn]:
        """Get all check-ins for a specific user.
        
        Args:
            user_id: The ID of the user.
            skip: Number of check-ins to skip.
            limit: Maximum number of check-ins to return.
            
        Returns:
            List of check-ins for the user.
        """
        if not ObjectId.is_valid(user_id):
            return []
            
        cursor = self.collection.find({"user_id": ObjectId(user_id)}).sort("check_date", -1).skip(skip).limit(limit)
        checkins = [CheckIn(**checkin) async for checkin in cursor]
        return checkins
    
    async def get_by_event(self, event_id: str, skip: int = 0, limit: int = 100) -> List[CheckIn]:
        """Get all check-ins for a specific event.
        
        Args:
            event_id: The ID of the event.
            skip: Number of check-ins to skip.
            limit: Maximum number of check-ins to return.
            
        Returns:
            List of check-ins for the event.
        """
        if not ObjectId.is_valid(event_id):
            return []
            
        cursor = self.collection.find({"event_id": ObjectId(event_id)}).sort("check_date", -1).skip(skip).limit(limit)
        checkins = [CheckIn(**checkin) async for checkin in cursor]
        return checkins
    
    async def get_latest_checkin(self, user_id: str, event_id: str) -> Optional[CheckIn]:
        """Get the latest check-in for a specific user and event.
        
        Args:
            user_id: The ID of the user.
            event_id: The ID of the event.
            
        Returns:
            The latest check-in if found, None otherwise.
        """
        if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(event_id):
            return None
            
        checkin_data = await self.collection.find_one(
            {
                "user_id": ObjectId(user_id),
                "event_id": ObjectId(event_id)
            },
            sort=[("check_date", -1)]
        )
        
        if checkin_data:
            return CheckIn(**checkin_data)
        return None
    
    async def check_already_checked_in_today(self, user_id: str, event_id: str) -> bool:
        """Check if a user has already checked in to an event today.
        
        Args:
            user_id: The ID of the user.
            event_id: The ID of the event.
            
        Returns:
            True if the user has already checked in today, False otherwise.
        """
        if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(event_id):
            return False
            
        # Get today's date range (start of day to end of day)
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        count = await self.collection.count_documents({
            "user_id": ObjectId(user_id),
            "event_id": ObjectId(event_id),
            "check_date": {"$gte": today, "$lt": tomorrow}
        })
        
        return count > 0
    
    async def _calculate_streak(self, user_id: str, event_id: str) -> int:
        """Calculate the current streak for a user and event.
        
        Args:
            user_id: The ID of the user.
            event_id: The ID of the event.
            
        Returns:
            The current streak count.
        """
        if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(event_id):
            return 1  # Default to 1 for new streaks
            
        latest_checkin = await self.get_latest_checkin(user_id, event_id)
        
        if not latest_checkin:
            return 1  # First check-in
            
        # Check if the latest check-in was yesterday or today
        latest_date = latest_checkin.check_date.replace(hour=0, minute=0, second=0, microsecond=0)
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        
        if latest_date == today:
            # Already checked in today, maintain the streak
            return latest_checkin.streak_count
        elif latest_date == yesterday:
            # Checked in yesterday, increment the streak
            return latest_checkin.streak_count + 1
        else:
            # Streak broken, start a new one
            return 1
    
    async def get_user_event_streak(self, user_id: str, event_id: str) -> UserEventStreak:
        """Get the streak information for a user and event.
        
        Args:
            user_id: The ID of the user.
            event_id: The ID of the event.
            
        Returns:
            The streak information.
        """
        if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(event_id):
            raise BadRequestException(detail="Invalid user or event ID")
            
        # Get the latest check-in to determine current streak
        latest_checkin = await self.get_latest_checkin(user_id, event_id)
        
        if not latest_checkin:
            # No check-ins yet
            return UserEventStreak(
                user_id=user_id,
                event_id=event_id,
                current_streak=0,
                longest_streak=0,
                last_check_date=datetime.utcnow()
            )
            
        # Find the longest streak by aggregating check-ins
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id), "event_id": ObjectId(event_id)}},
            {"$sort": {"streak_count": -1}},
            {"$limit": 1}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        longest_streak_data = await cursor.to_list(length=1)
        
        longest_streak = 0
        if longest_streak_data:
            longest_streak = longest_streak_data[0]["streak_count"]
        
        # Calculate current streak
        current_streak = await self._calculate_streak(user_id, event_id)
        if latest_checkin.check_date.date() == datetime.utcnow().date():
            # If checked in today, use the streak from the check-in
            current_streak = latest_checkin.streak_count
        
        return UserEventStreak(
            user_id=user_id,
            event_id=event_id,
            current_streak=current_streak,
            longest_streak=max(longest_streak, current_streak),
            last_check_date=latest_checkin.check_date
        )
    
    async def get_user_streaks(self, user_id: str) -> List[UserEventStreak]:
        """Get all streak information for a user across all events.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            List of streak information for each event the user has checked in to.
        """
        if not ObjectId.is_valid(user_id):
            return []
            
        # Get all events the user has checked in to
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id)}},
            {"$group": {"_id": "$event_id"}}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        event_ids = await cursor.to_list(length=100)
        
        # Get streak information for each event
        streaks = []
        for event_data in event_ids:
            event_id = str(event_data["_id"])
            streak = await self.get_user_event_streak(user_id, event_id)
            streaks.append(streak)
            
        return streaks