from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.models.event import Event
from app.core.exceptions import NotFoundException

class EventRepository:
    """Repository for Event model database operations.
    
    This class handles all database interactions for the Event model.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.events
    
    async def get_by_id(self, event_id: str) -> Optional[Event]:
        """Get an event by ID.
        
        Args:
            event_id: The ID of the event to retrieve.
            
        Returns:
            The event if found, None otherwise.
        """
        if not ObjectId.is_valid(event_id):
            return None
            
        event_data = await self.collection.find_one({"_id": ObjectId(event_id)})
        if event_data:
            return Event(**event_data)
        return None
    
    async def create(self, event: Event) -> Event:
        """Create a new event.
        
        Args:
            event: The event to create.
            
        Returns:
            The created event with ID.
        """
        event_dict = event.model_dump(exclude={"id"})
        result = await self.collection.insert_one(event_dict)
        event.id = result.inserted_id
        return event
    
    async def update(self, event_id: str, update_data: dict) -> Event:
        """Update an event.
        
        Args:
            event_id: The ID of the event to update.
            update_data: The data to update.
            
        Returns:
            The updated event.
            
        Raises:
            NotFoundException: If the event is not found.
        """
        if not ObjectId.is_valid(event_id):
            raise NotFoundException(detail=f"Invalid event ID: {event_id}")
            
        # Add updated_at timestamp
        update_data["updated_at"] = Event.updated_at.default_factory()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise NotFoundException(detail=f"Event with ID {event_id} not found")
            
        return await self.get_by_id(event_id)
    
    async def delete(self, event_id: str) -> bool:
        """Delete an event.
        
        Args:
            event_id: The ID of the event to delete.
            
        Returns:
            True if the event was deleted, False otherwise.
        """
        if not ObjectId.is_valid(event_id):
            return False
            
        result = await self.collection.delete_one({"_id": ObjectId(event_id)})
        return result.deleted_count > 0
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Event]:
        """Get all events with pagination.
        
        Args:
            skip: Number of events to skip.
            limit: Maximum number of events to return.
            
        Returns:
            List of events.
        """
        cursor = self.collection.find().skip(skip).limit(limit)
        events = [Event(**event) async for event in cursor]
        return events
    
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
    
    async def increment_checkins(self, event_id: str) -> Event:
        """Increment the total check-ins count for an event.
        
        Args:
            event_id: The ID of the event to update.
            
        Returns:
            The updated event.
            
        Raises:
            NotFoundException: If the event is not found.
        """
        if not ObjectId.is_valid(event_id):
            raise NotFoundException(detail=f"Invalid event ID: {event_id}")
            
        result = await self.collection.update_one(
            {"_id": ObjectId(event_id)},
            {
                "$inc": {"total_checkins": 1},
                "$set": {"updated_at": Event.updated_at.default_factory()}
            }
        )
        
        if result.matched_count == 0:
            raise NotFoundException(detail=f"Event with ID {event_id} not found")
            
        return await self.get_by_id(event_id)
    
    async def get_popular_events(self, limit: int = 10) -> List[Event]:
        """Get events sorted by number of participants.
        
        Args:
            limit: Maximum number of events to return.
            
        Returns:
            List of events sorted by popularity.
        """
        pipeline = [
            {"$addFields": {"participant_count": {"$size": "$participants"}}},
            {"$sort": {"participant_count": -1, "total_checkins": -1}},
            {"$limit": limit}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        events = [Event(**event) async for event in cursor]
        return events