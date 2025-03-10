from datetime import datetime
from typing import Any, Dict, Optional
from bson import ObjectId
from pydantic import BaseModel, Field
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic models.

    This allows us to use MongoDB's ObjectId with Pydantic models.
    """

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema(
                    [
                        core_schema.str_schema(),
                        core_schema.no_info_plain_validator_function(cls.validate),
                    ]
                ),
            ]
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class BaseDBModel(BaseModel):
    """Base model for all database models.

    This provides common fields and functionality for all models.
    """

    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, datetime: lambda dt: dt.isoformat()},
    }

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Convert model to dictionary, handling ObjectId conversion."""
        exclude_none = kwargs.pop("exclude_none", True)
        result = super().model_dump(exclude_none=exclude_none, **kwargs)

        # Convert ObjectId to string
        if "_id" in result and result["_id"] is not None:
            result["_id"] = str(result["_id"])

        return result

    # For backward compatibility
    def dict(self, **kwargs) -> Dict[str, Any]:
        """Legacy method for backward compatibility."""
        return self.model_dump(**kwargs)
