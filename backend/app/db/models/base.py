from datetime import datetime
from typing import Any, Dict, Optional
from bson import ObjectId
from pydantic import BaseModel, Field

class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic models.
    
    This allows us to use MongoDB's ObjectId with Pydantic models.
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class BaseDBModel(BaseModel):
    """Base model for all database models.
    
    This provides common fields and functionality for all models.
    """
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }

    def dict(self, **kwargs) -> Dict[str, Any]:
        """Convert model to dictionary, handling ObjectId conversion."""
        exclude_none = kwargs.pop("exclude_none", True)
        result = super().dict(exclude_none=exclude_none, **kwargs)
        
        # Convert ObjectId to string
        if "_id" in result and result["_id"] is not None:
            result["_id"] = str(result["_id"])
            
        return result