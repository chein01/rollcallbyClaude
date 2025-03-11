from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Boolean, Integer, DateTime, JSON
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr, Field

from app.db.models.base import BaseDBModel, BasePydanticModel


class User(BaseDBModel):
    """User model for authentication and profile information.

    This model stores user credentials and profile data.
    """

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(100), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    profile_image = Column(String(255), nullable=True)
    bio = Column(String(500), nullable=True)
    last_login = Column(DateTime, nullable=True)

    # Achievement tracking
    total_checkins = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    achievements = Column(JSON, default=list, nullable=False)

    # Relationships
    checkins = relationship("CheckIn", back_populates="user")
    created_events = relationship(
        "Event", back_populates="creator", foreign_keys="[Event.creator_id]"
    )
    participating_events = relationship(
        "Event", secondary="event_participants", back_populates="participants"
    )
    event_invitations = relationship(
        "Event", secondary="event_invited_users", back_populates="invited_users"
    )


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    profile_image: Optional[str] = None
    bio: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user information in API responses."""

    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    profile_image: Optional[str] = None
    bio: Optional[str] = None
    total_checkins: int
    longest_streak: int
    current_streak: int
    achievements: List[str]
    created_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "username": "johndoe",
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "profile_image": "https://example.com/profile.jpg",
                "bio": "I love tracking my daily activities!",
                "total_checkins": 42,
                "longest_streak": 30,
                "current_streak": 15,
                "achievements": ["7_day_streak", "first_event_created"],
                "created_at": "2023-01-01T00:00:00",
            }
        }
    }
