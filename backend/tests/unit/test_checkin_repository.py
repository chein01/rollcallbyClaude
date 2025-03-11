import pytest
from bson import ObjectId
from datetime import datetime, timedelta

from app.db.models.checkin import CheckIn
from app.core.exceptions import NotFoundException

pytestmark = pytest.mark.asyncio


class TestCheckInRepository:
    async def test_create_checkin(self, checkin_repository, test_user, test_event):
        # Arrange
        checkin = CheckIn(
            user_id=test_user.id,
            event_id=test_event.id,
            note="New test check-in",
            mood="excited"
        )
        
        # Act
        created_checkin = await checkin_repository.create(checkin)
        
        # Assert
        assert created_checkin.id is not None
        assert str(created_checkin.user_id) == str(test_user.id)
        assert str(created_checkin.event_id) == str(test_event.id)
        assert created_checkin.note == "New test check-in"
        assert created_checkin.mood == "excited"
        assert created_checkin.created_at is not None
        assert created_checkin.check_date is not None
    
    async def test_get_by_id(self, checkin_repository, test_checkin):
        # Act
        retrieved_checkin = await checkin_repository.get_by_id(str(test_checkin.id))
        
        # Assert
        assert retrieved_checkin is not None
        assert str(retrieved_checkin.id) == str(test_checkin.id)
        assert str(retrieved_checkin.user_id) == str(test_checkin.user_id)
    
    async def test_get_by_id_not_found(self, checkin_repository):
        # Act
        non_existent_id = str(ObjectId())
        retrieved_checkin = await checkin_repository.get_by_id(non_existent_id)
        
        # Assert
        assert retrieved_checkin is None
    
    async def test_get_all(self, checkin_repository, test_checkin):
        # Act
        checkins = await checkin_repository.get_all()
        
        # Assert
        assert len(checkins) >= 1
        assert any(str(checkin.id) == str(test_checkin.id) for checkin in checkins)
    
    async def test_get_by_user_id(self, checkin_repository, test_checkin, test_user):
        # Act
        user_checkins = await checkin_repository.get_by_user_id(str(test_user.id))
        
        # Assert
        assert len(user_checkins) >= 1
        assert any(str(checkin.id) == str(test_checkin.id) for checkin in user_checkins)
    
    async def test_get_by_event_id(self, checkin_repository, test_checkin, test_event):
        # Act
        event_checkins = await checkin_repository.get_by_event_id(str(test_event.id))
        
        # Assert
        assert len(event_checkins) >= 1
        assert any(str(checkin.id) == str(test_checkin.id) for checkin in event_checkins)
    
    async def test_get_latest_by_user_id(self, checkin_repository, test_user, test_event):
        # Arrange
        # Create multiple check-ins with different dates
        checkin1 = CheckIn(
            user_id=test_user.id,
            event_id=test_event.id,
            note="Older check-in",
            mood="happy",
            check_date=datetime.utcnow() - timedelta(days=2)
        )
        await checkin_repository.create(checkin1)
        
        checkin2 = CheckIn(
            user_id=test_user.id,
            event_id=test_event.id,
            note="Latest check-in",
            mood="excited",
            check_date=datetime.utcnow()
        )
        latest_checkin = await checkin_repository.create(checkin2)
        
        # Act
        retrieved_latest = await checkin_repository.get_latest_by_user_id(str(test_user.id))
        
        # Assert
        assert retrieved_latest is not None
        assert str(retrieved_latest.id) == str(latest_checkin.id)
        assert retrieved_latest.note == "Latest check-in"
    
    async def test_get_latest_checkin(self, checkin_repository, test_user, test_event):
        # Arrange
        # Create multiple check-ins with different dates
        checkin1 = CheckIn(
            user_id=test_user.id,
            event_id=test_event.id,
            note="Older check-in",
            mood="happy",
            check_date=datetime.utcnow() - timedelta(days=2)
        )
        await checkin_repository.create(checkin1)
        
        checkin2 = CheckIn(
            user_id=test_user.id,
            event_id=test_event.id,
            note="Latest check-in",
            mood="excited",
            check_date=datetime.utcnow()
        )
        latest_checkin = await checkin_repository.create(checkin2)
        
        # Act
        retrieved_latest = await checkin_repository.get_latest_checkin(str(test_user.id), str(test_event.id))
        
        # Assert
        assert retrieved_latest is not None
        assert str(retrieved_latest.id) == str(latest_checkin.id)
        assert retrieved_latest.note == "Latest check-in"
    
    async def test_check_already_checked_in_today(self, checkin_repository, test_user, test_event):
        # Arrange
        # Create a check-in for today
        today_checkin = CheckIn(
            user_id=test_user.id,
            event_id=test_event.id,
            note="Today's check-in",
            mood="happy",
            check_date=datetime.utcnow()
        )
        await checkin_repository.create(today_checkin)
        
        # Act
        already_checked_in = await checkin_repository.check_already_checked_in_today(
            str(test_user.id), str(test_event.id)
        )
        
        # Assert
        assert already_checked_in is True
        
        # Test with a different event (should return False)
        different_event_id = str(ObjectId())
        already_checked_in_different = await checkin_repository.check_already_checked_in_today(
            str(test_user.id), different_event_id
        )
        assert already_checked_in_different is False
    
    async def test_get_user_event_streak(self, checkin_repository, test_user, test_event):
        # Arrange
        # Create a series of consecutive daily check-ins
        today = datetime.utcnow().replace(hour=12, minute=0, second=0, microsecond=0)
        
        # Create check-ins for the past 3 days
        for i in range(3, 0, -1):
            checkin = CheckIn(
                user_id=test_user.id,
                event_id=test_event.id,
                note=f"Check-in {i} days ago",
                mood="happy",
                check_date=today - timedelta(days=i)
            )
            await checkin_repository.create(checkin)
        
        # Create today's check-in
        today_checkin = CheckIn(
            user_id=test_user.id,
            event_id=test_event.id,
            note="Today's check-in",
            mood="happy",
            check_date=today
        )
        await checkin_repository.create(today_checkin)
        
        # Act
        streak = await checkin_repository.get_user_event_streak(str(test_user.id), str(test_event.id))
        
        # Assert
        assert streak is not None
        assert streak.current_streak == 4  # 3 previous days + today
        assert streak.longest_streak == 4
        assert streak.user_id == str(test_user.id)
        assert streak.event_id == str(test_event.id)
    
    async def test_get_user_streaks(self, checkin_repository, test_user, test_event):
        # Arrange
        # Create check-ins for the test event
        today = datetime.utcnow().replace(hour=12, minute=0, second=0, microsecond=0)
        
        # Create check-ins for the past 3 days
        for i in range(3, 0, -1):
            checkin = CheckIn(
                user_id=test_user.id,
                event_id=test_event.id,
                note=f"Check-in {i} days ago",
                mood="happy",
                check_date=today - timedelta(days=i)
            )
            await checkin_repository.create(checkin)
        
        # Create today's check-in
        today_checkin = CheckIn(
            user_id=test_user.id,
            event_id=test_event.id,
            note="Today's check-in",
            mood="happy",
            check_date=today
        )
        await checkin_repository.create(today_checkin)
        
        # Create a second event and some check-ins for it
        second_event_id = ObjectId()
        for i in range(2, 0, -1):
            checkin = CheckIn(
                user_id=test_user.id,
                event_id=second_event_id,
                note=f"Event 2 check-in {i} days ago",
                mood="happy",
                check_date=today - timedelta(days=i)
            )
            await checkin_repository.create(checkin)
        
        # Act
        streaks = await checkin_repository.get_user_streaks(str(test_user.id))
        
        # Assert
        assert len(streaks) == 2  # Should have streaks for both events
        
        # Find the streak for the test event
        test_event_streak = next((s for s in streaks if s.event_id == str(test_event.id)), None)
        assert test_event_streak is not None
        assert test_event_streak.current_streak == 4
        
        # Find the streak for the second event
        second_event_streak = next((s for s in streaks if s.event_id == str(second_event_id)), None)
        assert second_event_streak is not None
        assert second_event_streak.current_streak == 0  # Broken streak (no check-in today)
        assert second_event_streak.longest_streak == 2