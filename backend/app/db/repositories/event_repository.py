from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.event import Event, EventCreate, EventUpdate
from app.core.exceptions import NotFoundException
from app.db.repositories.base_repository import BaseRepository


class EventRepository(BaseRepository[Event, EventCreate, EventUpdate]):
    """Repository for Event model database operations.

    This class handles all database interactions for the Event model.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.model_class = Event

    async def get_by_creator(
        self, creator_id: str, skip: int = 0, limit: int = 100
    ) -> List[Event]:
        """Get all events created by a specific user.

        Args:
            creator_id: The ID of the creator.
            skip: Number of events to skip.
            limit: Maximum number of events to return.

        Returns:
            List of events created by the user.
        """
        query = (
            select(self.model_class)
            .where(self.model_class.creator_id == creator_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_participant(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Event]:
        """Get all events a user is participating in.

        Args:
            user_id: The ID of the user.
            skip: Number of events to skip.
            limit: Maximum number of events to return.

        Returns:
            List of events the user is participating in.
        """
        # Use SQLAlchemy relationship query
        query = (
            select(self.model_class)
            .join(self.model_class.participants)
            .where(self.model_class.participants.any(id=user_id))
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return result.scalars().all()

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
        # Get the event
        event = await self.get_by_id(event_id)
        if not event:
            raise NotFoundException(detail=f"Event with ID {event_id} not found")

        # Get the user from User model
        from app.db.models.user import User

        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalars().first()

        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")

        # Add user to participants if not already there
        if user not in event.participants:
            event.participants.append(user)
            await self.db.commit()
            await self.db.refresh(event)

        return event

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
        # Get the event
        event = await self.get_by_id(event_id)
        if not event:
            raise NotFoundException(detail=f"Event with ID {event_id} not found")

        # Get the user from User model
        from app.db.models.user import User

        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalars().first()

        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")

        # Remove user from participants if present
        if user in event.participants:
            event.participants.remove(user)
            await self.db.commit()
            await self.db.refresh(event)

        return event

    async def increment_checkins(
        self, event_id: str, user_id: str, streak_count: int
    ) -> Event:
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
        # Get current event to check if we need to update streak leaders
        event = await self.get_by_id(event_id)
        if not event:
            raise NotFoundException(detail=f"Event with ID {event_id} not found")

        # Increment total check-ins
        event.total_checkins += 1
        event.updated_at = Event.updated_at.default_factory()

        # Update highest streak if needed
        if streak_count > event.highest_streak:
            event.highest_streak = streak_count
            event.streak_leaders = [user_id]
        elif (
            streak_count == event.highest_streak and user_id not in event.streak_leaders
        ):
            # Add user to streak leaders if they match the highest streak
            event.streak_leaders.append(user_id)

        # Commit changes
        await self.db.commit()
        await self.db.refresh(event)

        # Calculate and update average streak
        await self._update_avg_streak(event_id)

        return event

    async def get_popular_events(self, limit: int = 10) -> List[Event]:
        """Get events sorted by number of participants.

        Args:
            limit: Maximum number of events to return.

        Returns:
            List of events sorted by popularity.
        """
        from sqlalchemy import func, desc
        from sqlalchemy.orm import selectinload

        # Query for public events with participant count
        query = (
            select(self.model_class)
            .where(self.model_class.is_public == True)
            .options(selectinload(self.model_class.participants))
            .order_by(
                desc(func.count(self.model_class.participants)),
                desc(self.model_class.total_checkins),
            )
            .limit(limit)
        )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_streak_leaderboard(
        self, event_id: str, limit: int = 10
    ) -> List[dict]:
        """Get the streak leaderboard for an event.

        Args:
            event_id: The ID of the event.
            limit: Maximum number of users to return.

        Returns:
            List of users with their streak information, sorted by streak length.
        """
        from sqlalchemy import func, desc
        from app.db.models.checkin import CheckIn

        # Get the latest check-in for each user in this event using SQLAlchemy
        subquery = (
            select(CheckIn.user_id, func.max(CheckIn.check_date).label("latest_date"))
            .where(CheckIn.event_id == event_id)
            .group_by(CheckIn.user_id)
            .subquery()
        )

        query = (
            select(
                CheckIn.user_id,
                CheckIn.streak_count,
                CheckIn.check_date.label("last_check_date"),
            )
            .join(
                subquery,
                (CheckIn.user_id == subquery.c.user_id)
                & (CheckIn.check_date == subquery.c.latest_date),
            )
            .where(CheckIn.event_id == event_id)
            .order_by(desc(CheckIn.streak_count))
            .limit(limit)
        )

        result = await self.db.execute(query)
        rows = result.all()

        # Convert to dictionary format for API response
        leaderboard = [
            {
                "user_id": str(row.user_id),  # Ensure user_id is always a string
                "streak_count": row.streak_count,
                "last_check_date": row.last_check_date,
            }
            for row in rows
        ]

        return leaderboard

    async def get_total_checkins_leaderboard(
        self, event_id: str, limit: int = 10
    ) -> List[dict]:
        """Get the total check-ins leaderboard for an event.

        Args:
            event_id: The ID of the event.
            limit: Maximum number of users to return.

        Returns:
            List of users with their total check-ins, sorted by count.
        """
        from sqlalchemy import func, desc
        from app.db.models.checkin import CheckIn

        # Get total check-ins for each user in this event using SQLAlchemy
        query = (
            select(
                CheckIn.user_id,
                func.count(CheckIn.id).label("total_checkins"),
                func.max(CheckIn.check_date).label("last_check_date"),
            )
            .where(CheckIn.event_id == event_id)
            .group_by(CheckIn.user_id)
            .order_by(desc("total_checkins"))
            .limit(limit)
        )

        result = await self.db.execute(query)
        rows = result.all()

        # Convert to dictionary format for API response
        leaderboard = [
            {
                "user_id": str(row.user_id),  # Ensure user_id is always a string
                "total_checkins": row.total_checkins,
                "last_check_date": row.last_check_date,
            }
            for row in rows
        ]

        return leaderboard

    async def _update_avg_streak(self, event_id: str) -> None:
        """Update the average streak for an event.

        Args:
            event_id: The ID of the event.
        """
        from sqlalchemy import func
        from app.db.models.checkin import CheckIn

        # Get the latest check-in for each user in this event
        subquery = (
            select(CheckIn.user_id, func.max(CheckIn.check_date).label("latest_date"))
            .where(CheckIn.event_id == event_id)
            .group_by(CheckIn.user_id)
            .subquery()
        )

        # Calculate average streak from latest check-ins
        query = (
            select(func.avg(CheckIn.streak_count).label("avg_streak"))
            .join(
                subquery,
                (CheckIn.user_id == subquery.c.user_id)
                & (CheckIn.check_date == subquery.c.latest_date),
            )
            .where(CheckIn.event_id == event_id)
        )

        result = await self.db.execute(query)
        row = result.first()

        if row and row.avg_streak is not None:
            # Get the event to update
            event = await self.get_by_id(event_id)
            if event:
                # Update the average streak
                event.avg_streak = int(row.avg_streak)
                await self.db.commit()

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
            {"_id": ObjectId(event_id), "invited_users": {"$ne": ObjectId(user_id)}},
            {
                "$push": {"invited_users": ObjectId(user_id)},
                "$set": {"updated_at": Event.updated_at.default_factory()},
            },
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
                "$set": {"updated_at": Event.updated_at.default_factory()},
            },
        )

        if result.matched_count == 0:
            raise NotFoundException(detail=f"Event with ID {event_id} not found")

        return await self.get_by_id(event_id)
