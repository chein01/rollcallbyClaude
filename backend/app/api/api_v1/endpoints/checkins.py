from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId

from app.db.models.checkin import Checkin
from app.db.repositories.checkin_repository import CheckinRepository
from app.db.repositories.user_repository import UserRepository
from app.schemas.checkin import CheckinCreate, CheckinResponse

router = APIRouter()

# Dependencies
async def get_checkin_repository():
    from app.main import app
    return CheckinRepository(app.mongodb)

async def get_user_repository():
    from app.main import app
    return UserRepository(app.mongodb)

@router.post("/", response_model=CheckinResponse, status_code=status.HTTP_201_CREATED)
async def create_checkin(
    checkin: CheckinCreate,
    checkin_repo: CheckinRepository = Depends(get_checkin_repository),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Create a new check-in for a user."""
    # Verify user exists
    user = await user_repo.get_by_id(checkin.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {checkin.user_id} not found"
        )
    
    # Create check-in
    new_checkin = Checkin(
        user_id=ObjectId(checkin.user_id),
        timestamp=datetime.utcnow(),
        location=checkin.location,
        notes=checkin.notes
    )
    
    created_checkin = await checkin_repo.create(new_checkin)
    
    # Update user streak
    yesterday = datetime.utcnow() - timedelta(days=1)
    last_checkin = await checkin_repo.get_last_checkin_before(user.id, yesterday)
    
    # If last check-in was yesterday, increment streak
    if last_checkin and (yesterday.date() - last_checkin.timestamp.date()).days <= 1:
        await user_repo.update_streak(str(user.id), user.current_streak + 1, user.longest_streak)
    else:
        # Reset streak if no check-in yesterday
        await user_repo.update_streak(str(user.id), 1, user.longest_streak)
    
    # Increment total check-in count
    await user_repo.increment_checkin_count(str(user.id))
    
    return created_checkin

@router.get("/", response_model=List[CheckinResponse])
async def get_checkins(
    user_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    repo: CheckinRepository = Depends(get_checkin_repository)
):
    """Get all check-ins with optional filtering by user ID."""
    if user_id:
        return await repo.get_by_user_id(user_id, skip=skip, limit=limit)
    return await repo.get_all(skip=skip, limit=limit)

@router.get("/{checkin_id}", response_model=CheckinResponse)
async def get_checkin(
    checkin_id: str,
    repo: CheckinRepository = Depends(get_checkin_repository)
):
    """Get a specific check-in by ID."""
    checkin = await repo.get_by_id(checkin_id)
    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Check-in with ID {checkin_id} not found"
        )
    return checkin

@router.get("/user/{user_id}/latest", response_model=CheckinResponse)
async def get_latest_checkin(
    user_id: str,
    repo: CheckinRepository = Depends(get_checkin_repository)
):
    """Get the latest check-in for a specific user."""
    checkin = await repo.get_latest_by_user_id(user_id)
    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No check-ins found for user with ID {user_id}"
        )
    return checkin

@router.delete("/{checkin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checkin(
    checkin_id: str,
    repo: CheckinRepository = Depends(get_checkin_repository)
):
    """Delete a check-in."""
    deleted = await repo.delete(checkin_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Check-in with ID {checkin_id} not found"
        )
    return None