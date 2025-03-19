from datetime import datetime, timedelta
from typing import Any, Optional, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token.

    Args:
        subject: The subject of the token, typically the user ID.
        expires_delta: Optional expiration time delta. If not provided, the default from settings is used.

    Returns:
        The encoded JWT token.
    """
    if expires_delta:
        expire = int((datetime.utcnow() + expires_delta).timestamp())
    else:
        expire = int(
            (
                datetime.utcnow()
                + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            ).timestamp()
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.

    Args:
        plain_password: The plain-text password.
        hashed_password: The hashed password to compare against.

    Returns:
        True if the password matches the hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password.

    Args:
        password: The plain-text password to hash.

    Returns:
        The hashed password.
    """
    return pwd_context.hash(password)


def decode_token(token: str) -> dict:
    """Decode a JWT token.

    Args:
        token: The JWT token to decode.

    Returns:
        The decoded token payload.

    Raises:
        jwt.JWTError: If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # Convert timestamp to datetime for easier handling
        if "exp" in payload:
            payload["exp"] = datetime.fromtimestamp(payload["exp"])
        return payload
    except jwt.JWTError:
        raise jwt.JWTError("Invalid token")
