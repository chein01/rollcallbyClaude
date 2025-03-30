from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import Column, Integer, BigInteger, text
from sqlalchemy.ext.declarative import declared_attr
from pydantic import BaseModel, field_serializer

from app.db.database import Base


class BaseDBModel(Base):
    """Base model for all database models.

    This provides common fields and functionality for all models.
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        BigInteger,
        default=lambda: int(datetime.utcnow().timestamp()),
        nullable=False,
    )
    updated_at = Column(
        BigInteger,
        default=lambda: int(datetime.utcnow().timestamp()),
        onupdate=lambda: int(datetime.utcnow().timestamp()),
        nullable=False,
    )

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically from class name."""
        return cls.__name__.lower()


class TimestampModel(BaseModel):
    """Base model for handling timestamp serialization.

    This model provides common functionality for handling timestamp fields.
    All models that need to handle timestamp fields should inherit from this class.
    """

    model_config = {"from_attributes": True}

    @field_serializer("*")
    def serialize_timestamp(self, value: Any, _info) -> Any:
        """Return timestamp value as is since it's already in Unix timestamp format."""
        return value


class BasePydanticModel(BaseModel):
    """Base Pydantic model for all API schemas.

    This provides common functionality for all API schemas.
    """

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }

    def dict(self, **kwargs) -> Dict[str, Any]:
        """Legacy method for backward compatibility."""
        return self.model_dump(**kwargs)
