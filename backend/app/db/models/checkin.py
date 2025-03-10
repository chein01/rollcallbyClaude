from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.db.models.base import BaseDBModel, PyObjectId

class CheckIn(BaseDBModel):
    """Check-in model for tracking daily user activity.
    
    This model represents a user checking in to an event on a specific day.
    """
    user_id: PyObjectId = Field(...)
    event_id: PyObjectId = Field(...)
    check_date: datetime = Field(default_factory=datetime.utcnow)
    note: Optional[str] = Field(None, max_length=500)  # Optional note for the check-in
    mood: Optional[str] = Field(None, max_length=50)  # Optional mood indicator
    streak_count: int = Field(default=1)  # Current streak count at time of check-in
    
    class Config:
        collection = "checkins"
        schema_extra = {
            "example": {
                "user_id": "60d5e1c7a0f5a5a5a5a5a5a5",
                "event_id": "60d5e1c7a0f5a5a5a5a5a5a7",
                "check_date": "2023-01-01T10:30:00",
                "note": "Completed 45 minutes of coding today!",
                "mood": "productive",
                "streak_count": 7
            }
        }


class CheckInCreate(BaseModel):
    """Schema for creating a new check-in."""
    event_id: str = Field(...)
    note: Optional[str] = Field(None, max_length=500)
    mood: Optional[str] = Field(None, max_length=50)


class CheckInResponse(BaseModel):
    """Schema for check-in information in API responses."""
    id: str
    user_id: str
    event_id: str
    check_date: datetime
    note: Optional[str] = None
    mood: Optional[str] = None
    streak_count: int
    created_at: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "id": "60d5e1c7a0f5a5a5a5a5a5a8",
                "user_id": "60d5e1c7a0f5a5a5a5a5a5a5",
                "event_id": "60d5e1c7a0f5a5a5a5a5a5a7",
                "check_date": "2023-01-01T10:30:00",
                "note": "Completed 45 minutes of coding today!",
                "mood": "productive",
                "streak_count": 7,
                "created_at": "2023-01-01T10:30:00"
            }
        }


class UserEventStreak(BaseModel):
    """Schema for tracking a user's streak for a specific event."""
    user_id: str
    event_id: str
    current_streak: int
    longest_streak: int
    last_check_date: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "60d5e1c7a0f5a5a5a5a5a5a5",
                "event_id": "60d5e1c7a0f5a5a5a5a5a5a7",
                "current_streak": 7,
                "longest_streak": 30,
                "last_check_date": "2023-01-01T10:30:00"
            }
        }