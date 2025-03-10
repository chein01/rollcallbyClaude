from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

from app.db.models.base import BaseDBModel, PyObjectId

class User(BaseDBModel):
    """User model for authentication and profile information.
    
    This model stores user credentials and profile data.
    """
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(...)
    hashed_password: str = Field(...)
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    profile_image: Optional[str] = None
    bio: Optional[str] = None
    last_login: Optional[datetime] = None
    
    # Achievement tracking
    total_checkins: int = Field(default=0)
    longest_streak: int = Field(default=0)
    current_streak: int = Field(default=0)
    achievements: List[str] = Field(default_factory=list)
    
    model_config = {
        "collection": "users",
        "json_schema_extra": {
            "example": {
                "username": "johndoe",
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "profile_image": "https://example.com/profile.jpg",
                "bio": "I love tracking my daily activities!",
                "total_checkins": 42,
                "longest_streak": 30,
                "current_streak": 15,
                "achievements": ["7_day_streak", "first_event_created"]
            }
        }
    }


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
    id: str
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
                "id": "60d5e1c7a0f5a5a5a5a5a5a5",
                "username": "johndoe",
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "profile_image": "https://example.com/profile.jpg",
                "bio": "I love tracking my daily activities!",
                "total_checkins": 42,
                "longest_streak": 30,
                "current_streak": 15,
                "achievements": ["7_day_streak", "first_event_created"],
                "created_at": "2023-01-01T00:00:00"
            }
        }
    }