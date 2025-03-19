from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import random
import string
from pydantic import BaseModel, EmailStr, constr, Field

from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    decode_token,
)
from app.core.config import settings
from app.db.database import get_db
from app.db.repositories.user_repository import UserRepository
from app.core.email import send_reset_password_email

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


class LoginRequest(BaseModel):
    """Schema for login request."""

    username_or_email: str = Field(..., min_length=1)  # Có thể là username hoặc email
    password: str


async def get_user_repository(db: AsyncSession = Depends(get_db)):
    return UserRepository(db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """
    Validate access token and return current user.

    Args:
        token: JWT token
        user_repo: Repository to interact with database

    Returns:
        Current user

    Raises:
        HTTPException: If token is invalid or user does not exist
    """
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account is deactivated"
        )

    return user


@router.post("/login")
async def login(
    login_data: LoginRequest, user_repo: UserRepository = Depends(get_user_repository)
):
    """
    Login user and return access token.
    Can login with username or email.

    Args:
        login_data: Login data containing username/email and password
        user_repo: Repository to interact with database

    Returns:
        Access token and user information
    """
    # Try to find user by email first
    user = await user_repo.get_by_email(login_data.username_or_email)

    # If not found by email, try to find by username
    if not user:
        user = await user_repo.get_by_username(login_data.username_or_email)

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account is deactivated"
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
        },
    }


@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """
    Logout user.
    In this case, we just return a success message
    as the JWT token will automatically expire after ACCESS_TOKEN_EXPIRE_MINUTES.

    Args:
        token: Current JWT token
        user_repo: Repository to interact with database

    Returns:
        Logout success message
    """
    return {"message": "Successfully logged out"}


@router.post("/forgot-password")
async def forgot_password(
    email: str,
    background_tasks: BackgroundTasks,
    user_repo: UserRepository = Depends(get_user_repository),
):
    """
    Send password recovery email.

    Args:
        email: User's email
        background_tasks: FastAPI background tasks
        user_repo: Repository to interact with database

    Returns:
        Message indicating password recovery email has been sent
    """
    user = await user_repo.get_by_email(email)
    if not user:
        # Return success even if email doesn't exist to prevent email enumeration
        return {
            "message": "If the email exists, you will receive password recovery instructions"
        }

    # Create reset token
    reset_token = "".join(random.choices(string.ascii_letters + string.digits, k=32))
    reset_token_expires = timedelta(hours=1)

    # Save reset token to database
    await user_repo.update_reset_token(user.id, reset_token, reset_token_expires)

    # Send email in background
    background_tasks.add_task(
        send_reset_password_email, email=user.email, reset_token=reset_token
    )

    return {
        "message": "If the email exists, you will receive password recovery instructions"
    }


@router.post("/reset-password")
async def reset_password(
    reset_token: str,
    new_password: str,
    user_repo: UserRepository = Depends(get_user_repository),
):
    """
    Reset password with new password.

    Args:
        reset_token: Password reset token
        new_password: New password
        user_repo: Repository to interact with database

    Returns:
        Message indicating password has been reset successfully
    """
    # Check reset token
    user = await user_repo.get_by_reset_token(reset_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Update new password
    hashed_password = get_password_hash(new_password)
    await user_repo.update_password(user.id, hashed_password)

    return {"message": "Password has been reset successfully"}
