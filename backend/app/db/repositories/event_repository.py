from typing import List, Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.models.event import Event, EventCreate, EventUpdate
from app.core.exceptions import NotFoundException
from app.db.repositories.base_repository import BaseRepository

class EventRepository(BaseRepository[Event, EventCreate, EventUpdate]):
    """Repository for Event model database operations.
    
    This class handles all database interactions for the Event model.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.events
        self.model_class = Event
    

    
    async def get_by_creator(self, creator_id: str, skip: int = 0, limit: int = 100) -> List[Event]:
        """Get all events created by a specific user.
        
        Args:
            creator_id: The ID of the creator.
            skip: Number of events to skip.
            limit: Maximum number of events to return.
            
        Returns:
            List of events created by the user.
        """
        if not ObjectId.is_valid(creator_id):
            return []
            
        cursor = self.collection.find({"creator_id": ObjectId(creator_id)}).skip(skip).limit(limit)
        events = [Event(**event) async for event in cursor]
        return events
    
    async def get_by_participant(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Event]:
        """Get all events a user is participating in.
        
        Args:
            user_id: The ID of the user.
            skip: Number of events to skip.
            limit: Maximum number of events to return.
            
        Returns:
            List of events the user is participating in.
        """
        if not ObjectId.is_valid(user_id):
            return []
            
        cursor = self.collection.find({"participants": ObjectId(user_id)}).skip(skip).limit(limit)
        events = [Event(**event) async for event in cursor]
        return events
    
    async def add_participant(self, event_id: str, user_id: str) -> Event:
        """Add a user as a participant to an event.
        
        Args:
            event_id: The ID of the event.
            user_id: The ID of the user to add.
            
        Returns:
            The updated event.
            
        Raises:
            NotFoundException: If the event is not found.
        """
        if not ObjectId.is_valid(event_id) or not ObjectId.is_valid(user_id):
            raise NotFoundException(detail="Invalid event or user ID")
            
        # Only add the user if they're not already a participant
        result = await self.collection.update_one(
            {
                "_id": ObjectId(event_id),
                "participants": {"$ne": ObjectId(user_id)}
            },
            {
                "$push": {"participants": ObjectId(user_id)},
                "$set": {"updated_at": Event.updated_at.default_factory()}
            }
        )
        
        if result.matched_count == 0:
            # Check if the event exists
            event = await self.get_by_id(event_id)
            if not event:
                raise NotFoundException(detail=f"Event with ID {event_id} not found")
                
        return await self.get_by_id(event_id)
    
    async def remove_participant(self, event_id: str, user_id: str) -> Event:
        """Remove a user as a participant from an event.
        
        Args:
            event_id: The ID of the event.
            user_id: The ID of the user to remove.
            
        Returns:
            The updated event.
            
        Raises:
            NotFoundException: If the event is not found.
        """
        if not ObjectId.is_valid(event_id) or not ObjectId.is_valid(user_id):
            raise NotFoundException(detail="Invalid event or user ID")
            
        result = await self.collection.update_one(
            {"_id": ObjectId(event_id)},
            {
                "$pull": {"participants": ObjectId(user_id)},
                "$set": {"updated_at": Event.updated_at.default_factory()}
            }
        )
        
        if result.matched_count == 0:
            raise NotFoundException(detail=f"Event with ID {event_id} not found")
            
        return await self.get_by_id(event_id)
    
    async def increment_checkins(self, event_id: str, user_id: str, streak_count: int) -> Event:
        """Increment the total check-ins count for an event and update streak statistics.
        
        Args:
            event_id: The ID of the event to update.
            user_id: The ID of the user who checked in.
            streak_count: The current streak count of the user.
            
        Returns:
            The updated event.
            
        Raises:
            NotFoundException: If the event is not found.
        """
        if not ObjectId.is_valid(event_id) or not ObjectId.is_valid(user_id):
            raise NotFoundException(detail=f"Invalid event or user ID")
            
        # Get current event to check if we need to update streak leaders
        event = await self.get_by_id(event_id)
        if not event:
            raise NotFoundException(detail=f"Event with ID {event_id} not found")
            
        update_data = {
            "total_checkins": 1,
            "updated_at": Event.updated_at.default_factory()
        }
        
        # Update highest streak if needed
        if streak_count > event.highest_streak:
            update_data["highest_streak"] = streak_count
            update_data["streak_leaders"] = [ObjectId(user_id)]
        elif streak_count == event.highest_streak and ObjectId(user_id) not in event.streak_leaders:
            # Add user to streak leaders if they match the highest streak
            result = await self.collection.update_one(
                {"_id": ObjectId(event_id)},
                {"$addToSet": {"streak_leaders": ObjectId(user_id)}}
            )
        
        # Increment check-ins and update other fields
        result = await self.collection.update_one(
            {"_id": ObjectId(event_id)},
            {
                "$inc": {"total_checkins": 1},
                "$set": {k: v for k, v in update_data.items() if k != "total_checkins"}
            }
        )
        
        # Calculate and update average streak
        await self._update_avg_streak(event_id)
        
        return await self.get_by_id(event_id)
    
    async def get_popular_events(self, limit: int = 10) -> List[Event]:
        """Get events sorted by number of participants.
        
        Args:
            limit: Maximum number of events to return.
            
        Returns:
            List of events sorted by popularity.
        """
        pipeline = [
            {"$match": {"is_public": True}},  # Only include public events
            {"$addFields": {"participant_count": {"$size": "$participants"}}},
            {"$sort": {"participant_count": -1, "total_checkins": -1}},
            {"$limit": limit}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        events = [Event(**event) async for event in cursor]
        return events
        
    async def get_streak_leaderboard(self, event_id: str, limit: int = 10) -> List[dict]:
        """Get the streak leaderboard for an event.
        
        Args:
            event_id: The ID of the event.
            limit: Maximum number of users to return.
            
        Returns:
            List of users with their streak information, sorted by streak length.
        """
        if not ObjectId.is_valid(event_id):
            return []
            
        # Get the latest check-in for each user in this event
        pipeline = [
            {"$match": {"event_id": ObjectId(event_id)}},
            {"$sort": {"check_date": -1}},
            {"$group": {
                "_id": "$user_id",
                "latest_checkin": {"$first": "$$ROOT"},
            }},
            {"$project": {
                "user_id": "$_id",
                "streak_count": "$latest_checkin.streak_count",
                "last_check_date": "$latest_checkin.check_date"
            }},
            {"$sort": {"streak_count": -1}},
            {"$limit": limit}
        ]
        
        cursor = self.db.checkins.aggregate(pipeline)
        leaderboard = await cursor.to_list(length=limit)
        return leaderboard
        
    async def get_total_checkins_leaderboard(self, event_id: str, limit: int = 10) -> List[dict]:
        """Get the total check-ins leaderboard for an event.
        
        Args:
            event_id: The ID of the event.
            limit: Maximum number of users to return.
            
        Returns:
            List of users with their total check-ins, sorted by count.
        """
        if not ObjectId.is_valid(event_id):
            return []
            
        pipeline = [
            {"$match": {"event_id": ObjectId(event_id)}},
            {"$group": {
                "_id": "$user_id",
                "total_checkins": {"$sum": 1},
                "last_check_date": {"$max": "$check_date"}
            }},
            {"$project": {
                "user_id": "$_id",
                "total_checkins": 1,
                "last_check_date": 1
            }},
            {"$sort": {"total_checkins": -1}},
            {"$limit": limit}
        ]
        
        cursor = self.db.checkins.aggregate(pipeline)
        leaderboard = await cursor.to_list(length=limit)
        return leaderboard
        
    async def _update_avg_streak(self, event_id: str) -> None:
        """Update the average streak for an event.
        
        Args:
            event_id: The ID of the event.
        """
        if not ObjectId.is_valid(event_id):
            return
            
        pipeline = [
            {"$match": {"event_id": ObjectId(event_id)}},
            {"$sort": {"check_date": -1}},
            {"$group": {
                "_id": "$user_id",
                "latest_streak": {"$first": "$streak_count"}
            }},
            {"$group": {
                "_id": None,
                "avg_streak": {"$avg": "$latest_streak"}
            }}
        ]
        
        cursor = self.db.checkins.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        
        if result:
            avg_streak = int(result[0]["avg_streak"])
            await self.collection.update_one(
                {"_id": ObjectId(event_id)},
                {"$set": {"avg_streak": avg_streak}}
            )
            
    async def invite_user(self, event_id: str, user_id: str) -> Event:
        """Invite a user to an event.
        
        Args:
            event_id: The ID of the event.
            user_id: The ID of the user to invite.
            
        Returns:
            The updated event.
            
        Raises:
            NotFoundException: If the event is not found.
        """
        if not ObjectId.is_valid(event_id) or not ObjectId.is_valid(user_id):
            raise NotFoundException(detail="Invalid event or user ID")
            
        # Only add the user if they're not already invited
        result = await self.collection.update_one(
            {
                "_id": ObjectId(event_id),
                "invited_users": {"$ne": ObjectId(user_id)}
            },
            {
                "$push": {"invited_users": ObjectId(user_id)},
                "$set": {"updated_at": Event.updated_at.default_factory()}
            }
        )
        
        if result.matched_count == 0:
            # Check if the event exists
            event = await self.get_by_id(event_id)
            if not event:
                raise NotFoundException(detail=f"Event with ID {event_id} not found")
                
        return await self.get_by_id(event_id)
        
    async def remove_invitation(self, event_id: str, user_id: str) -> Event:
        """Remove a user's invitation to an event.
        
        Args:
            event_id: The ID of the event.
            user_id: The ID of the user whose invitation to remove.
            
        Returns:
            The updated event.
            
        Raises:
            NotFoundException: If the event is not found.
        """
        if not ObjectId.is_valid(event_id) or not ObjectId.is_valid(user_id):
            raise NotFoundException(detail="Invalid event or user ID")
            
        result = await self.collection.update_one(
            {"_id": ObjectId(event_id)},
            {
                "$pull": {"invited_users": ObjectId(user_id)},
                "$set": {"updated_at": Event.updated_at.default_factory()}
            }
        )
        
        if result.matched_count == 0:
            raise NotFoundException(detail=f"Event with ID {event_id} not found")
            
        return await self.get_by_id(event_id)