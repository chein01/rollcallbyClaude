from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.event import Event, EventCreate, EventUpdate, EventResponse
from app.db.repositories.event_repository import EventRepository
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.checkin_repository import CheckInRepository
from app.db.models.checkin import UserEventStreak
from app.db.database import get_db

router = APIRouter()


# Dependencies
async def get_event_repository(db: AsyncSession = Depends(get_db)):
    return EventRepository(db)


async def get_user_repository(db: AsyncSession = Depends(get_db)):
    return UserRepository(db)


async def get_checkin_repository(db: AsyncSession = Depends(get_db)):
    return CheckInRepository(db)


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event: EventCreate,
    current_user_id: int,
    repo: EventRepository = Depends(get_event_repository),
):
    """Create a new event."""
    # Create event with current user as creator
    new_event = Event(
        **event.model_dump(),
        creator_id=current_user_id,
        participants=[current_user_id]  # Creator is automatically a participant
    )
    
    created_event = await repo.create(new_event)
    return created_event


@router.get("/", response_model=List[EventResponse])
async def get_events(
    skip: int = 0, 
    limit: int = 100, 
    repo: EventRepository = Depends(get_event_repository)
):
    """Get all public events with pagination."""
    return await repo.get_public_events(skip=skip, limit=limit)


@router.get("/my", response_model=List[EventResponse])
async def get_my_events(
    current_user_id: int,
    skip: int = 0, 
    limit: int = 100, 
    repo: EventRepository = Depends(get_event_repository)
):
    """Get all events created by the current user."""
    return await repo.get_by_creator(current_user_id, skip=skip, limit=limit)


@router.get("/participating", response_model=List[EventResponse])
async def get_participating_events(
    current_user_id: int,
    skip: int = 0, 
    limit: int = 100, 
    repo: EventRepository = Depends(get_event_repository)
):
    """Get all events the current user is participating in."""
    return await repo.get_by_participant(current_user_id, skip=skip, limit=limit)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int, 
    repo: EventRepository = Depends(get_event_repository)
):
    """Get a specific event by ID."""
    event = await repo.get_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )
    return event


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_update: EventUpdate,
    current_user_id: int,
    repo: EventRepository = Depends(get_event_repository),
):
    """Update an event's information."""
    # Check if user is the creator of the event
    event = await repo.get_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )
    
    if event.creator_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator can update this event"
        )
    
    try:
        updated_event = await repo.update(event_id, event_update.model_dump(exclude_unset=True))
        return updated_event
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int, 
    current_user_id: int,
    repo: EventRepository = Depends(get_event_repository)
):
    """Delete an event."""
    # Check if user is the creator of the event
    event = await repo.get_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )
    
    if event.creator_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator can delete this event"
        )
    
    deleted = await repo.delete(event_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )
    return None


@router.post("/{event_id}/join", response_model=EventResponse)
async def join_event(
    event_id: int,
    current_user_id: int,
    repo: EventRepository = Depends(get_event_repository),
):
    """Join an event as a participant."""
    try:
        updated_event = await repo.add_participant(event_id, current_user_id)
        return updated_event
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{event_id}/leave", response_model=EventResponse)
async def leave_event(
    event_id: int,
    current_user_id: int,
    repo: EventRepository = Depends(get_event_repository),
):
    """Leave an event as a participant."""
    # Check if user is the creator of the event
    event = await repo.get_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )
    
    if event.creator_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The creator cannot leave the event"
        )
    
    try:
        updated_event = await repo.remove_participant(event_id, current_user_id)
        return updated_event
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{event_id}/leaderboard", response_model=List[UserEventStreak])
async def get_event_leaderboard(
    event_id: int,
    limit: int = 10,
    repo: CheckInRepository = Depends(get_checkin_repository),
):
    """Get leaderboard for a specific event."""
    # Get all participants' streaks for this event
    # This would need to be implemented in the CheckInRepository
    try:
        return await repo.get_event_leaderboard(event_id, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{event_id}/invite/{user_id}", response_model=EventResponse)
async def invite_user(
    event_id: int,
    user_id: int,
    current_user_id: int,
    repo: EventRepository = Depends(get_event_repository),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """Invite a user to an event."""
    # Check if user exists
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Check if current user is the creator or a participant
    event = await repo.get_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )
    
    if event.creator_id != current_user_id and current_user_id not in event.participants:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator or participants can invite users"
        )
    
    try:
        updated_event = await repo.add_invited_user(event_id, user_id)
        return updated_event
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))