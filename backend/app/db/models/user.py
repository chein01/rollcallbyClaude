from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Boolean, Integer, BigInteger, JSON
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr, Field

from app.db.models.base import BaseDBModel, TimestampModel
from app.db.models.streak_freeze import StreakFreeze


class User(BaseDBModel):
    """User model for storing user information."""

    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    reset_token = Column(String(255), unique=True, index=True, nullable=True)
    reset_token_expires_at = Column(BigInteger, nullable=True)  # Unix timestamp
    last_login = Column(BigInteger, nullable=True)  # Unix timestamp

    # Relationships
    created_events = relationship(
        "Event", back_populates="creator", foreign_keys="Event.creator_id"
    )
    participating_events = relationship(
        "Event", secondary="event_participants", back_populates="participants"
    )
    event_invitations = relationship(
        "Event", secondary="event_invited_users", back_populates="invited_users"
    )
    checkins = relationship("CheckIn", back_populates="user")
    streak_freezes = relationship("StreakFreeze", back_populates="user")


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserResponse(TimestampModel):
    """Schema for user information in API responses."""

    id: int
    username: str
    email: str
    is_active: bool
    is_superuser: bool
    reset_token: Optional[str] = None
    reset_token_expires_at: Optional[int] = None  # Unix timestamp
    last_login: Optional[int] = None  # Unix timestamp
    created_at: int  # Unix timestamp

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "is_active": True,
                "is_superuser": False,
                "reset_token": None,
                "reset_token_expires_at": None,
                "last_login": 1672531200,  # Unix timestamp for 2023-01-01T00:00:00
                "created_at": 1672531200,  # Unix timestamp for 2023-01-01T00:00:00
            }
        }
    }
