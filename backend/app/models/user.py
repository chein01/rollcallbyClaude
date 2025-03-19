from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger
from sqlalchemy.sql import func

from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires_at = Column(BigInteger, nullable=True)  # Unix timestamp
    created_at = Column(
        BigInteger, server_default=func.unix_timestamp()
    )  # Unix timestamp
    updated_at = Column(
        BigInteger, server_default=func.unix_timestamp(), onupdate=func.unix_timestamp()
    )  # Unix timestamp
