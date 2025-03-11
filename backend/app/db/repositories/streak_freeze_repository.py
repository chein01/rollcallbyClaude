from datetime import datetime
from typing import List, Optional
from bson import ObjectId

from app.db.models.streak_freeze import StreakFreeze, StreakFreezeCreate, StreakFreezeUpdate
from app.core.config import database
from app.db.repositories.base_repository import BaseRepository


class StreakFreezeRepository(BaseRepository[StreakFreeze, StreakFreezeCreate, StreakFreezeUpdate]):
    """Repository for streak freeze operations."""

    collection = database.streak_freezes
    model_class = StreakFreeze

    async def create_streak_freeze(self, user_id: str, streak_freeze: StreakFreezeCreate) -> StreakFreeze:
        """Create a new streak freeze for a user and event."""
        streak_freeze_data = streak_freeze.model_dump()
        streak_freeze_data["user_id"] = ObjectId(user_id)
        streak_freeze_data["event_id"] = ObjectId(streak_freeze.event_id)

        result = await self.collection.insert_one(streak_freeze_data)
        created_streak_freeze = await self.collection.find_one({"_id": result.inserted_id})
        return StreakFreeze(**created_streak_freeze)

    async def get_streak_freeze(self, streak_freeze_id: str) -> Optional[StreakFreeze]:
        """Get a streak freeze by ID."""
        return await self.get_by_id(streak_freeze_id)

    async def get_user_event_streak_freezes(self, user_id: str, event_id: str) -> List[StreakFreeze]:
        """Get all streak freezes for a user and event."""
        streak_freezes = []
        cursor = self.collection.find(
            {"user_id": ObjectId(user_id), "event_id": ObjectId(event_id)}
        )
        async for streak_freeze in cursor:
            streak_freezes.append(StreakFreeze(**streak_freeze))
        return streak_freezes

    async def get_available_streak_freezes(self, user_id: str, event_id: str) -> List[StreakFreeze]:
        """Get all unused streak freezes for a user and event."""
        streak_freezes = []
        now = datetime.utcnow()
        cursor = self.collection.find(
            {
                "user_id": ObjectId(user_id),
                "event_id": ObjectId(event_id),
                "is_used": False,
                "$or": [{"expiry_date": {"$gt": now}}, {"expiry_date": None}],
            }
        )
        async for streak_freeze in cursor:
            streak_freezes.append(StreakFreeze(**streak_freeze))
        return streak_freezes

    async def update_streak_freeze(self, streak_freeze_id: str, update_data: StreakFreezeUpdate) -> Optional[StreakFreeze]:
        """Update a streak freeze."""
        streak_freeze = await self.collection.find_one({"_id": ObjectId(streak_freeze_id)})
        if not streak_freeze:
            return None

        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        if update_dict:
            # If marking as used, set the used_date to now if not provided
            if update_dict.get("is_used") and "used_date" not in update_dict:
                update_dict["used_date"] = datetime.utcnow()

            await self.collection.update_one(
                {"_id": ObjectId(streak_freeze_id)}, {"$set": update_dict}
            )
            updated_streak_freeze = await self.collection.find_one(
                {"_id": ObjectId(streak_freeze_id)}
            )
            return StreakFreeze(**updated_streak_freeze)
        return StreakFreeze(**streak_freeze)

    async def delete_streak_freeze(self, streak_freeze_id: str) -> bool:
        """Delete a streak freeze."""
        return await self.delete(streak_freeze_id)

    async def use_streak_freeze(self, user_id: str, event_id: str) -> bool:
        """Use a streak freeze for a user and event.
        
        This will find the oldest available streak freeze and mark it as used.
        """
        available_freezes = await self.get_available_streak_freezes(user_id, event_id)
        if not available_freezes:
            return False

        # Sort by creation date and use the oldest one
        oldest_freeze = sorted(available_freezes, key=lambda x: x.created_at)[0]
        update_data = StreakFreezeUpdate(is_used=True, used_date=datetime.utcnow())
        updated_freeze = await self.update_streak_freeze(str(oldest_freeze.id), update_data)
        return updated_freeze is not None