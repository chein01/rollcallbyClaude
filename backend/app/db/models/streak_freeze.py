from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.db.models.base import BaseDBModel, PyObjectId


class StreakFreeze(BaseDBModel):
    """Streak Freeze model for allowing users to maintain their streak when missing a day.
    
    This model represents a streak freeze that a user can apply to prevent losing their streak.
    """
    
    user_id: PyObjectId = Field(...)
    event_id: PyObjectId = Field(...)
    used_date: Optional[datetime] = Field(None)  # When the freeze was applied
    is_used: bool = Field(default=False)  # Whether the freeze has been used
    expiry_date: Optional[datetime] = Field(None)  # Optional expiration date for the freeze
    
    model_config = {
        "collection": "streak_freezes",
        "json_schema_extra": {
            "example": {
                "user_id": "60d5e1c7a0f5a5a5a5a5a5a5",
                "event_id": "60d5e1c7a0f5a5a5a5a5a5a7",
                "used_date": "2023-01-15T00:00:00",
                "is_used": True,
                "expiry_date": "2023-02-15T00:00:00"
            }
        }
    }


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
    used_date: Optional[datetime] = None
    is_used: bool
    expiry_date: Optional[datetime] = None
    created_at: datetime
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "60d5e1c7a0f5a5a5a5a5a5a9",
                "user_id": "60d5e1c7a0f5a5a5a5a5a5a5",
                "event_id": "60d5e1c7a0f5a5a5a5a5a5a7",
                "used_date": "2023-01-15T00:00:00",
                "is_used": True,
                "expiry_date": "2023-02-15T00:00:00",
                "created_at": "2023-01-01T00:00:00"
            }
        }
    }