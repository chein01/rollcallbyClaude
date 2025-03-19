from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from datetime import datetime
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.base import BaseDBModel
from app.core.exceptions import NotFoundException

# Define type variables for the models
T = TypeVar("T", bound=BaseDBModel)
CreateT = TypeVar("CreateT")
UpdateT = TypeVar("UpdateT")


class BaseRepository(Generic[T, CreateT, UpdateT]):
    """Base repository for all database repositories.

    This class provides common CRUD operations for all repositories.

    Attributes:
        db: The database session.
        model_class: The SQLAlchemy model class for this repository.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.model_class: Type[T] = None  # Will be set by child classes

    async def get_by_id(self, id: int) -> Optional[T]:
        """Get a record by ID.

        Args:
            id: The ID of the record to retrieve.

        Returns:
            The record if found, None otherwise.
        """
        query = select(self.model_class).where(self.model_class.id == id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of records.
        """
        query = select(self.model_class).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, data: Union[CreateT, Dict[str, Any]]) -> T:
        """
        Create a new record.

        Args:
            data: The data to create the record with.

        Returns:
            The created record with ID.
        """
        if hasattr(data, "model_dump"):
            # If it's a Pydantic model
            create_data = data.model_dump(exclude_unset=True)
        elif hasattr(data, "dict"):
            # For backward compatibility
            create_data = data.dict(exclude_unset=True)
        elif isinstance(data, self.model_class):
            # If it's already a SQLAlchemy model instance
            db_obj = data
            self.db.add(db_obj)
            await self.db.commit()
            await self.db.refresh(db_obj)

            return db_obj
        else:
            create_data = data

        # Create new model instance
        db_obj = self.model_class(**create_data)

        # Add to session and commit
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)

        return db_obj

    async def update(self, id: int, update_data: Union[UpdateT, Dict[str, Any]]) -> T:
        """Update a record.

        Args:
            id: The ID of the record to update.
            update_data: The data to update.

        Returns:
            The updated record.

        Raises:
            NotFoundException: If the record is not found.
        """
        # Get the existing record
        db_obj = await self.get_by_id(id)
        if not db_obj:
            raise NotFoundException(
                detail=f"{self.model_class.__name__} with ID {id} not found"
            )

        # Convert model to dict if needed
        if hasattr(update_data, "model_dump"):
            update_dict = {
                k: v
                for k, v in update_data.model_dump(exclude_unset=True).items()
                if v is not None
            }
        elif hasattr(update_data, "dict"):
            # For backward compatibility
            update_dict = {
                k: v
                for k, v in update_data.dict(exclude_unset=True).items()
                if v is not None
            }
        else:
            update_dict = update_data

        # Update the record
        for key, value in update_dict.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)

        # Add updated_at timestamp
        if hasattr(db_obj, "updated_at"):
            setattr(db_obj, "updated_at", datetime.utcnow())

        # Commit changes
        await self.db.commit()
        await self.db.refresh(db_obj)

        return db_obj

    async def delete(self, id: int) -> bool:
        """Delete a record.

        Args:
            id: The ID of the record to delete.

        Returns:
            True if the record was deleted, False otherwise.
        """
        # Get the existing record
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return False

        # Delete the record
        await self.db.delete(db_obj)
        await self.db.commit()

        return True

    async def exists(self, id: int) -> bool:
        """Check if a record exists.

        Args:
            id: The ID of the record to check.

        Returns:
            True if the record exists, False otherwise.
        """
        query = select(self.model_class).where(self.model_class.id == id)
        result = await self.db.execute(query)
        return result.first() is not None

    async def count(self, filter_dict: Dict[str, Any] = None) -> int:
        """Count records matching a filter.

        Args:
            filter_dict: The filter to apply.

        Returns:
            The number of matching records.
        """
        query = select(self.model_class)

        if filter_dict:
            for key, value in filter_dict.items():
                if hasattr(self.model_class, key):
                    query = query.where(getattr(self.model_class, key) == value)

        result = await self.db.execute(query)
        return len(result.all())
