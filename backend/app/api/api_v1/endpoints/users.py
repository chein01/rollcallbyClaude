from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.db.models.user import User
from app.db.repositories.user_repository import UserRepository
from app.db.models.user import UserCreate, UserResponse, UserUpdate
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash

router = APIRouter()


# Dependency to get user repository
async def get_user_repository(db: AsyncSession = Depends(get_db)):
    return UserRepository(db)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate, repo: UserRepository = Depends(get_user_repository)
):
    """Create a new user."""
    # Check if user with email already exists
    existing_user = await repo.get_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Check if username is taken
    if user.username:
        existing_username = await repo.get_by_username(user.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

    # Create user with hashed password
    user_data = user.dict()
    user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    new_user = User(**user_data)
    created_user = await repo.create(new_user)
    return created_user


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0, limit: int = 100, repo: UserRepository = Depends(get_user_repository)
):
    """Get all users with pagination."""
    return await repo.get_all(skip=skip, limit=limit)


@router.get("/leaderboard", response_model=List[UserResponse])
async def get_leaderboard(
    limit: int = 10, repo: UserRepository = Depends(get_user_repository)
):
    """Get user leaderboard by streak."""
    return await repo.get_leaderboard(limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, repo: UserRepository = Depends(get_user_repository)):
    """Get a specific user by ID."""
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    repo: UserRepository = Depends(get_user_repository),
):
    """Update a user's information."""
    try:
        updated_user = await repo.update(user_id, user_update.dict(exclude_unset=True))
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int, repo: UserRepository = Depends(get_user_repository)
):
    """Delete a user."""
    deleted = await repo.delete(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    return None
