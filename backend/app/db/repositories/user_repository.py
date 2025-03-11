from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User, UserCreate, UserUpdate
from app.core.exceptions import NotFoundException
from app.db.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Repository for User model database operations.

    This class handles all database interactions for the User model.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.model_class = User

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email.

        Args:
            email: The email of the user to retrieve.

        Returns:
            The user if found, None otherwise.
        """
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username.

        Args:
            username: The username of the user to retrieve.

        Returns:
            The user if found, None otherwise.
        """
        query = select(User).where(User.username == username)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_leaderboard(self, limit: int = 10) -> List[User]:
        """Get users sorted by longest streak.

        Args:
            limit: Maximum number of users to return.

        Returns:
            List of users sorted by longest streak.
        """
        query = select(User).order_by(User.longest_streak.desc()).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_streak(
        self, user_id: int, current_streak: int, longest_streak: int
    ) -> User:
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
            "updated_at": User.updated_at.default_factory(),
        }

        # Only update longest_streak if the new streak is longer
        if longest_streak > 0:
            update_data["longest_streak"] = longest_streak

        # Get the user to update
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")

        # Update the user
        for key, value in update_data.items():
            setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def increment_checkins(self, user_id: int) -> User:
        """Increment a user's total check-ins count.

        Args:
            user_id: The ID of the user to update.

        Returns:
            The updated user.

        Raises:
            NotFoundException: If the user is not found.
        """
        # Get the user to update
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")

        # Increment total_checkins
        user.total_checkins += 1
        user.updated_at = User.updated_at.default_factory()

        # Commit changes
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def add_achievement(self, user_id: int, achievement: str) -> User:
        """Add an achievement to a user's achievements list.

        Args:
            user_id: The ID of the user to update.
            achievement: The achievement to add.

        Returns:
            The updated user.

        Raises:
            NotFoundException: If the user is not found.
        """
        # Get the user to update
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")

        # Only add the achievement if it's not already in the list
        achievements = user.achievements if user.achievements else []
        if achievement not in achievements:
            achievements.append(achievement)
            user.achievements = achievements
            user.updated_at = User.updated_at.default_factory()

            # Commit changes
            await self.db.commit()
            await self.db.refresh(user)

        return user
