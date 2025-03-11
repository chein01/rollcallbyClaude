from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship

from app.db.models.base import BaseDBModel, BasePydanticModel


# Association tables for many-to-many relationships
event_participants = Table(
    'event_participants',
    BaseDBModel.metadata,
    Column('event_id', Integer, ForeignKey('event.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True)
)

event_invited_users = Table(
    'event_invited_users',
    BaseDBModel.metadata,
    Column('event_id', Integer, ForeignKey('event.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True)
)

event_streak_leaders = Table(
    'event_streak_leaders',
    BaseDBModel.metadata,
    Column('event_id', Integer, ForeignKey('event.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True)
)

class Event(BaseDBModel):
    """Event model for tracking daily check-ins.

    This model represents an activity that users can check in to daily.
    """

    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    creator_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    category = Column(String(50), nullable=True)
    icon = Column(String(255), nullable=True)  # Icon identifier or URL
    is_public = Column(Boolean, default=False, nullable=False)  # Whether the event is visible to other users
    total_checkins = Column(Integer, default=0, nullable=False)  # Total number of check-ins across all participants
    avg_streak = Column(Integer, default=0, nullable=False)  # Average streak across all participants
    highest_streak = Column(Integer, default=0, nullable=False)  # Highest streak achieved in this event
    
    # Relationships
    creator = relationship("User", back_populates="created_events", foreign_keys=[creator_id])
    participants = relationship("User", secondary=event_participants, back_populates="participating_events")
    invited_users = relationship("User", secondary=event_invited_users, back_populates="event_invitations")
    streak_leaders = relationship("User", secondary=event_streak_leaders)
    checkins = relationship("CheckIn", back_populates="event", cascade="all, delete-orphan")


class EventCreate(BaseModel):
    """Schema for creating a new event."""

    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    icon: Optional[str] = None
    is_public: bool = Field(default=False)


class EventUpdate(BaseModel):
    """Schema for updating event information."""

    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    icon: Optional[str] = None
    is_public: Optional[bool] = None


class EventResponse(BaseModel):
    """Schema for event information in API responses."""

    id: int
    title: str
    description: Optional[str] = None
    creator_id: int
    category: Optional[str] = None
    icon: Optional[str] = None
    is_public: bool
    participants: List[int]
    invited_users: List[int] = Field(default_factory=list)
    total_checkins: int
    avg_streak: int = 0
    highest_streak: int = 0
    streak_leaders: List[int] = Field(default_factory=list)
    created_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "title": "Daily Coding Practice",
                "description": "Commit to coding at least 30 minutes every day",
                "creator_id": 1,
                "category": "Learning",
                "icon": "code",
                "is_public": False,
                "participants": [
                    1,
                    2,
                ],
                "invited_users": [
                    3,
                    4,
                ],
                "total_checkins": 156,
                "avg_streak": 12,
                "highest_streak": 30,
                "streak_leaders": [
                    1,
                    2,
                ],
                "created_at": "2023-01-01T00:00:00",
            }
        }
    }
