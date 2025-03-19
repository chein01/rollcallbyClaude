from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.checkin import CheckIn
from app.db.repositories.checkin_repository import CheckInRepository
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.event_repository import EventRepository
from app.db.models.checkin import CheckInCreate, CheckInResponse, UserEventStreak
from app.db.database import get_db
from app.api.api_v1.endpoints.auth import get_current_user
from app.db.models.user import User

router = APIRouter()


# Dependencies
async def get_checkin_repository(db: AsyncSession = Depends(get_db)):
    return CheckInRepository(db)


async def get_user_repository(db: AsyncSession = Depends(get_db)):
    return UserRepository(db)


@router.post("/", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
async def create_checkin(
    checkin: CheckInCreate,
    current_user_id: int,
    checkin_repo: CheckInRepository = Depends(get_checkin_repository),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """Create a new check-in for a user."""
    # Check if already checked in today
    already_checked_in = await checkin_repo.check_already_checked_in_today(
        current_user_id, checkin.event_id
    )
    if already_checked_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already checked in to this event today",
        )

    # Create check-in
    new_checkin = CheckIn(
        user_id=current_user_id,
        event_id=checkin.event_id,
        note=checkin.note,
        mood=checkin.mood,
    )

    created_checkin = await checkin_repo.create(new_checkin)

    # Increment total check-in count for the user
    await user_repo.increment_checkins(current_user_id)

    # Get the updated streak information
    streak = await checkin_repo.get_user_event_streak(current_user_id, checkin.event_id)

    # Update user's overall streak if needed
    if streak.current_streak > 0:
        await user_repo.update_streak(
            current_user_id, streak.current_streak, streak.longest_streak
        )

    return created_checkin


@router.get("/", response_model=List[CheckInResponse])
async def get_checkins(
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    repo: CheckInRepository = Depends(get_checkin_repository),
    current_user: User = Depends(get_current_user),
):
    """Get all check-ins with optional filtering by user ID."""
    # Only allow users to view their own check-ins
    if user_id and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view other users' check-ins",
        )

    if user_id:
        return await repo.get_by_user(user_id, skip=skip, limit=limit)
    return await repo.get_all(skip=skip, limit=limit)


@router.get("/{checkin_id}", response_model=CheckInResponse)
async def get_checkin(
    checkin_id: int, repo: CheckInRepository = Depends(get_checkin_repository)
):
    """Get a specific check-in by ID."""
    checkin = await repo.get_by_id(checkin_id)
    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Check-in with ID {checkin_id} not found",
        )
    return checkin


@router.get("/user/{user_id}/latest", response_model=CheckInResponse)
async def get_latest_checkin(
    user_id: int,
    repo: CheckInRepository = Depends(get_checkin_repository),
    current_user: User = Depends(get_current_user),
):
    """Get the latest check-in for a specific user."""
    # Only allow users to view their own latest check-in
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view other users' latest check-in",
        )

    checkin = await repo.get_latest_by_user(user_id)
    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No check-ins found for user with ID {user_id}",
        )
    return checkin


@router.get("/user/{user_id}/streaks", response_model=List[UserEventStreak])
async def get_user_streaks(
    user_id: int, repo: CheckInRepository = Depends(get_checkin_repository)
):
    """Get all streak information for a user across all events."""
    try:
        streaks = await repo.get_user_streaks(user_id)
        return streaks
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/user/{user_id}/event/{event_id}/streak", response_model=UserEventStreak)
async def get_user_event_streak(
    user_id: int,
    event_id: int,
    repo: CheckInRepository = Depends(get_checkin_repository),
):
    """Get streak information for a specific user and event."""
    try:
        streak = await repo.get_user_event_streak(user_id, event_id)
        return streak
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/user/{user_id}/event/{event_id}/streak-status")
async def get_streak_status(
    user_id: int,
    event_id: int,
    repo: CheckInRepository = Depends(get_checkin_repository),
):
    """Get the status of a user's streak for an event, including if it's at risk of being broken."""
    try:
        # Get the latest check-in
        latest_checkin = await repo.get_latest_checkin(user_id, event_id)
        if not latest_checkin:
            return {"status": "no_streak", "message": "No streak found for this event"}

        # Check if already checked in today
        already_checked_in = await repo.check_already_checked_in_today(
            user_id, event_id
        )

        # Get today's date and the date of the last check-in
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        last_check_date = latest_checkin.check_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # Calculate days since last check-in
        days_since_last_checkin = (today - last_check_date).days

        if already_checked_in:
            return {
                "status": "safe",
                "message": "You've already checked in today",
                "streak": latest_checkin.streak_count,
            }
        elif days_since_last_checkin == 0:
            # Same day but not checked in yet
            return {
                "status": "pending",
                "message": "Don't forget to check in today to maintain your streak",
                "streak": latest_checkin.streak_count,
            }
        elif days_since_last_checkin == 1:
            # Last check-in was yesterday
            return {
                "status": "warning",
                "message": "Check in today to keep your streak going!",
                "streak": latest_checkin.streak_count,
            }
        else:
            # Check if streak freeze is available
            from app.db.repositories.streak_freeze_repository import (
                StreakFreezeRepository,
            )

            streak_freeze_repo = StreakFreezeRepository()
            has_freeze = await streak_freeze_repo.has_available_freeze(
                user_id, event_id
            )

            if has_freeze:
                return {
                    "status": "danger",
                    "message": "Your streak will be broken unless you check in today! You have a streak freeze available.",
                    "streak": latest_checkin.streak_count,
                    "has_freeze": True,
                }
            else:
                return {
                    "status": "broken",
                    "message": "Your streak has been broken. Start a new streak by checking in today!",
                    "streak": 0,
                    "previous_streak": latest_checkin.streak_count,
                }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{checkin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checkin(
    checkin_id: str, repo: CheckInRepository = Depends(get_checkin_repository)
):
    """Delete a check-in."""
    deleted = await repo.delete(checkin_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Check-in with ID {checkin_id} not found",
        )
    return None
