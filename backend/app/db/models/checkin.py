from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.models.base import BaseDBModel


class CheckIn(BaseDBModel):
    """Check-in model for tracking daily user activity.
    This model represents a user checking in to an event on a specific day.
    """

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("event.id"), nullable=False)
    check_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    note = Column(String(500), nullable=True)  # Optional note for the check-in
    mood = Column(String(50), nullable=True)  # Optional mood indicator
    streak_count = Column(
        Integer, default=1, nullable=False
    )  # Current streak count at time of check-in

    # Relationships
    user = relationship("User", back_populates="checkins")
    event = relationship("Event", back_populates="checkins")


class CheckInCreate(BaseModel):
    """Schema for creating a new check-in."""

    event_id: int = Field(...)
    note: Optional[str] = Field(None, max_length=500)
    mood: Optional[str] = Field(None, max_length=50)


class CheckInResponse(BaseModel):
    """Schema for check-in information in API responses."""

    id: int
    user_id: int
    event_id: int
    check_date: datetime
    note: Optional[str] = None
    mood: Optional[str] = None
    streak_count: int
    created_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "user_id": 1,
                "event_id": 1,
                "check_date": "2023-01-01T10:30:00",
                "note": "Completed 45 minutes of coding today!",
                "mood": "productive",
                "streak_count": 7,
                "created_at": "2023-01-01T10:30:00",
            }
        }
    }


class UserEventStreak(BaseModel):
    """Schema for tracking a user's streak for a specific event."""

    user_id: int
    event_id: int
    current_streak: int
    longest_streak: int
    last_check_date: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "60d5e1c7a0f5a5a5a5a5a5a5",
                "event_id": "60d5e1c7a0f5a5a5a5a5a5a7",
                "current_streak": 7,
                "longest_streak": 30,
                "last_check_date": "2023-01-01T10:30:00",
            }
        }
    }
