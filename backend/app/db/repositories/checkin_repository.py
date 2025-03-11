from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.checkin import CheckIn, UserEventStreak
from app.core.exceptions import NotFoundException, BadRequestException
from app.db.repositories.base_repository import BaseRepository


class CheckInRepository(BaseRepository[CheckIn, CheckIn, Dict[str, Any]]):
    """Repository for CheckIn model database operations.

    This class handles all database interactions for the CheckIn model.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.model_class = CheckIn

    async def create(self, checkin: CheckIn) -> CheckIn:
        """Create a new check-in.

        Args:
            checkin: The check-in to create.

        Returns:
            The created check-in with ID.
        """
        # Calculate streak before saving
        streak_count = await self._calculate_streak(
            checkin.user_id, checkin.event_id
        )
        checkin.streak_count = streak_count

        # Use the parent class's create method
        return await super().create(checkin)

    async def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[CheckIn]:
        """Get check-ins for a specific user.

        Args:
            user_id: The ID of the user.
            skip: Number of check-ins to skip.
            limit: Maximum number of check-ins to return.

        Returns:
            List of check-ins for the user.
        """
        query = (
            select(self.model_class)
            .where(self.model_class.user_id == user_id)
            .order_by(self.model_class.check_date.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_event(
        self, event_id: int, skip: int = 0, limit: int = 100
    ) -> List[CheckIn]:
        """Get check-ins for a specific event.

        Args:
            event_id: The ID of the event.
            skip: Number of check-ins to skip.
            limit: Maximum number of check-ins to return.

        Returns:
            List of check-ins for the event.
        """
        query = (
            select(self.model_class)
            .where(self.model_class.event_id == event_id)
            .order_by(self.model_class.check_date.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_user_and_event(
        self, user_id: int, event_id: int, skip: int = 0, limit: int = 100
    ) -> List[CheckIn]:
        """Get check-ins for a specific user and event.

        Args:
            user_id: The ID of the user.
            event_id: The ID of the event.
            skip: Number of check-ins to skip.
            limit: Maximum number of check-ins to return.

        Returns:
            List of check-ins for the user and event.
        """
        query = (
            select(self.model_class)
            .where(
                and_(
                    self.model_class.user_id == user_id,
                    self.model_class.event_id == event_id,
                )
            )
            .order_by(self.model_class.check_date.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_latest_by_user_and_event(
        self, user_id: int, event_id: int
    ) -> Optional[CheckIn]:
        """Get the latest check-in for a specific user and event.

        Args:
            user_id: The ID of the user.
            event_id: The ID of the event.

        Returns:
            The latest check-in if found, None otherwise.
        """
        query = (
            select(self.model_class)
            .where(
                and_(
                    self.model_class.user_id == user_id,
                    self.model_class.event_id == event_id,
                )
            )
            .order_by(self.model_class.check_date.desc())
            .limit(1)
        )

        result = await self.db.execute(query)
        return result.scalars().first()

    async def _calculate_streak(self, user_id: int, event_id: int) -> int:
        """Calculate the current streak for a user and event.

        Args:
            user_id: The ID of the user.
            event_id: The ID of the event.

        Returns:
            The current streak count.
        """
        # Get the latest check-in
        latest_checkin = await self.get_latest_by_user_and_event(user_id, event_id)

        # If no previous check-ins, streak is 1
        if not latest_checkin:
            return 1

        # Check if the latest check-in was yesterday or today
        today = datetime.utcnow().date()
        latest_date = latest_checkin.check_date.date()

        # If the latest check-in was today, maintain the same streak
        if latest_date == today:
            return latest_checkin.streak_count

        # If the latest check-in was yesterday, increment streak
        if latest_date == today - timedelta(days=1):
            return latest_checkin.streak_count + 1

        # Otherwise, streak is broken, start at 1
        return 1

    async def get_user_event_streak(
        self, user_id: int, event_id: int
    ) -> UserEventStreak:
        """Get the streak information for a user and event.

        Args:
            user_id: The ID of the user.
            event_id: The ID of the event.

        Returns:
            UserEventStreak object with streak information.
        """
        # Get all check-ins for this user and event
        checkins = await self.get_by_user_and_event(user_id, event_id)

        if not checkins:
            return UserEventStreak(
                user_id=user_id,
                event_id=event_id,
                current_streak=0,
                longest_streak=0,
                last_check_date=datetime.utcnow(),
            )

        # Sort by date
        checkins.sort(key=lambda x: x.check_date)

        # Get the latest check-in
        latest_checkin = checkins[-1]

        # Calculate current streak
        current_streak = latest_checkin.streak_count

        # Calculate longest streak
        longest_streak = max(c.streak_count for c in checkins)

        return UserEventStreak(
            user_id=str(user_id),
            event_id=str(event_id),
            current_streak=current_streak,
            longest_streak=longest_streak,
            last_check_date=latest_checkin.check_date,
        )

    async def get_user_streaks(self, user_id: str) -> List[UserEventStreak]:
        """Get all streak information for a user across all events.

        Args:
            user_id: The ID of the user.

        Returns:
            List of UserEventStreak objects.
        """
        # Get all check-ins for this user
        query = select(self.model_class).where(self.model_class.user_id == user_id)

        result = await self.db.execute(query)
        checkins = result.scalars().all()

        # Group by event_id
        event_checkins = {}
        for checkin in checkins:
            if checkin.event_id not in event_checkins:
                event_checkins[checkin.event_id] = []
            event_checkins[checkin.event_id].append(checkin)

        # Calculate streaks for each event
        streaks = []
        for event_id, event_checkins_list in event_checkins.items():
            # Sort by date
            event_checkins_list.sort(key=lambda x: x.check_date)

            # Get the latest check-in
            latest_checkin = event_checkins_list[-1]

            # Calculate current streak
            current_streak = latest_checkin.streak_count

            # Calculate longest streak
            longest_streak = max(c.streak_count for c in event_checkins_list)

            streaks.append(
                UserEventStreak(
                    user_id=user_id,
                    event_id=str(event_id),
                    current_streak=current_streak,
                    longest_streak=longest_streak,
                    last_check_date=latest_checkin.check_date,
                )
            )

        return streaks

    async def get_event_streaks(
        self, event_id: str, limit: int = 10
    ) -> List[UserEventStreak]:
        """Get streak information for all users in an event.

        Args:
            event_id: The ID of the event.
            limit: Maximum number of streaks to return.

        Returns:
            List of UserEventStreak objects sorted by current streak.
        """
        # Get all check-ins for this event
        query = select(self.model_class).where(self.model_class.event_id == event_id)

        result = await self.db.execute(query)
        checkins = result.scalars().all()

        # Group by user_id
        user_checkins = {}
        for checkin in checkins:
            if checkin.user_id not in user_checkins:
                user_checkins[checkin.user_id] = []
            user_checkins[checkin.user_id].append(checkin)

        # Calculate streaks for each user
        streaks = []
        for user_id, user_checkins_list in user_checkins.items():
            # Sort by date
            user_checkins_list.sort(key=lambda x: x.check_date)

            # Get the latest check-in
            latest_checkin = user_checkins_list[-1]

            # Calculate current streak
            current_streak = latest_checkin.streak_count

            # Calculate longest streak
            longest_streak = max(c.streak_count for c in user_checkins_list)

            streaks.append(
                UserEventStreak(
                    user_id=str(user_id),
                    event_id=event_id,
                    current_streak=current_streak,
                    longest_streak=longest_streak,
                    last_check_date=latest_checkin.check_date,
                )
            )

        # Sort by current streak (descending)
        streaks.sort(key=lambda x: x.current_streak, reverse=True)

        # Return top streaks
        return streaks[:limit]
