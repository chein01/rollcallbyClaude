from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from pydantic import BaseModel, Field

from app.db.database import Base


class BaseDBModel(Base):
    """Base model for all database models.

    This provides common fields and functionality for all models.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically from class name."""
        return cls.__name__.lower()


class BasePydanticModel(BaseModel):
    """Base Pydantic model for all API schemas.

    This provides common functionality for all API schemas.
    """
    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
        "json_encoders": {datetime: lambda dt: dt.isoformat()}
    }

    def dict(self, **kwargs) -> Dict[str, Any]:
        """Legacy method for backward compatibility."""
        return self.model_dump(**kwargs)
