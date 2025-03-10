from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.db.models.base import BaseDBModel, PyObjectId


class Event(BaseDBModel):
    """Event model for tracking daily check-ins.

    This model represents an activity that users can check in to daily.
    """

    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    creator_id: PyObjectId = Field(...)
    category: Optional[str] = Field(None, max_length=50)
    icon: Optional[str] = Field(None)  # Icon identifier or URL
    is_public: bool = Field(default=True)  # Whether the event is visible to other users
    participants: List[PyObjectId] = Field(
        default_factory=list
    )  # Users who joined this event
    total_checkins: int = Field(
        default=0
    )  # Total number of check-ins across all participants

    model_config = {
        "collection": "events",
        "json_schema_extra": {
            "example": {
                "title": "Daily Coding Practice",
                "description": "Commit to coding at least 30 minutes every day",
                "creator_id": "60d5e1c7a0f5a5a5a5a5a5a5",
                "category": "Learning",
                "icon": "code",
                "is_public": True,
                "participants": [
                    "60d5e1c7a0f5a5a5a5a5a5a5",
                    "60d5e1c7a0f5a5a5a5a5a5a6",
                ],
                "total_checkins": 156,
            }
        }
    }


class EventCreate(BaseModel):
    """Schema for creating a new event."""

    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    icon: Optional[str] = None
    is_public: bool = Field(default=True)


class EventUpdate(BaseModel):
    """Schema for updating event information."""

    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    icon: Optional[str] = None
    is_public: Optional[bool] = None


class EventResponse(BaseModel):
    """Schema for event information in API responses."""

    id: str
    title: str
    description: Optional[str] = None
    creator_id: str
    category: Optional[str] = None
    icon: Optional[str] = None
    is_public: bool
    participants: List[str]
    total_checkins: int
    created_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "60d5e1c7a0f5a5a5a5a5a5a7",
                "title": "Daily Coding Practice",
                "description": "Commit to coding at least 30 minutes every day",
                "creator_id": "60d5e1c7a0f5a5a5a5a5a5a5",
                "category": "Learning",
                "icon": "code",
                "is_public": True,
                "participants": [
                    "60d5e1c7a0f5a5a5a5a5a5a5",
                    "60d5e1c7a0f5a5a5a5a5a5a6",
                ],
                "total_checkins": 156,
                "created_at": "2023-01-01T00:00:00",
            }
        }
    }
