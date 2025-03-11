from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.models.checkin import CheckIn, UserEventStreak
from app.core.exceptions import NotFoundException, BadRequestException
from app.db.repositories.base_repository import BaseRepository

class CheckInRepository(BaseRepository[CheckIn, CheckIn, Dict[str, Any]]):
    """Repository for CheckIn model database operations.
    
    This class handles all database interactions for the CheckIn model.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.checkins
        self.model_class = CheckIn
    
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
        
        # Use the parent class's create method
        return await super().create(checkin)
    
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
            # Check if a streak freeze is available and can be used
            from app.db.repositories.streak_freeze_repository import StreakFreezeRepository
            streak_freeze_repo = StreakFreezeRepository()
            freeze_used = await streak_freeze_repo.use_streak_freeze(user_id, event_id)
            
            if freeze_used:
                # Streak freeze was used, maintain the streak but don't increment
                return latest_checkin.streak_count
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
        
    async def get_event_leaderboard(self, event_id: str, limit: int = 10) -> List[UserEventStreak]:
        """Get leaderboard data for a specific event.
        
        Args:
            event_id: The ID of the event.
            limit: Maximum number of users to return.
            
        Returns:
            List of user streak information for the event, sorted by current streak.
        """
        if not ObjectId.is_valid(event_id):
            return []
            
        # Get all users who have checked in to this event
        pipeline = [
            {"$match": {"event_id": ObjectId(event_id)}},
            {"$group": {"_id": "$user_id"}}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        user_ids = await cursor.to_list(length=100)
        
        # Get streak information for each user
        streaks = []
        for user_data in user_ids:
            user_id = str(user_data["_id"])
            streak = await self.get_user_event_streak(user_id, event_id)
            streaks.append(streak)
            
        # Sort by current streak (descending)
        streaks.sort(key=lambda x: x.current_streak, reverse=True)
        
        # Return top users
        return streaks[:limit]