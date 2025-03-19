from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.db.models.base import BaseDBModel, BasePydanticModel


class StreakFreeze(BaseDBModel):
    """Streak Freeze model for allowing users to maintain their streak when missing a day.

    This model represents a streak freeze that a user can apply to prevent losing their streak.
    """

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("event.id"), nullable=False)
    used_date = Column(DateTime, nullable=True)  # When the freeze was applied
    is_used = Column(
        Boolean, default=False, nullable=False
    )  # Whether the freeze has been used
    expiry_date = Column(
        DateTime, nullable=True
    )  # Optional expiration date for the freeze

    # Relationships
    user = relationship("User", backref="streak_freezes")
    event = relationship("Event", backref="streak_freezes")


class StreakFreezeCreate(BaseModel):
    """Schema for creating a new streak freeze."""

    event_id: str = Field(...)
    expiry_date: Optional[datetime] = Field(None)


class StreakFreezeUpdate(BaseModel):
    """Schema for updating a streak freeze."""

    is_used: Optional[bool] = None
    used_date: Optional[datetime] = None


class StreakFreezeResponse(BaseModel):
    """Schema for streak freeze information in API responses."""

    id: str
    user_id: str
    event_id: str
    used_date: Optional[int] = None  # Unix timestamp
    is_used: bool
    expiry_date: Optional[int] = None  # Unix timestamp
    created_at: int  # Unix timestamp

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "60d5e1c7a0f5a5a5a5a5a5a9",
                "user_id": "60d5e1c7a0f5a5a5a5a5a5a5",
                "event_id": "60d5e1c7a0f5a5a5a5a5a5a7",
                "used_date": 1673740800,  # Unix timestamp for 2023-01-15T00:00:00
                "is_used": True,
                "expiry_date": 1676419200,  # Unix timestamp for 2023-02-15T00:00:00
                "created_at": 1672531200,  # Unix timestamp for 2023-01-01T00:00:00
            }
        }
    }
