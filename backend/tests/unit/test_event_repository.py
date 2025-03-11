import pytest
from bson import ObjectId
from datetime import datetime

from app.db.models.event import Event, EventCreate, EventUpdate
from app.core.exceptions import NotFoundException

pytestmark = pytest.mark.asyncio


class TestEventRepository:
    async def test_create_event(self, event_repository, test_user):
        # Arrange
        event = Event(
            name="New Test Event",
            description="A new test event for testing",
            creator_id=test_user.id,
            participants=[test_user.id],
            is_public=True,
            frequency="daily"
        )
        
        # Act
        created_event = await event_repository.create(event)
        
        # Assert
        assert created_event.id is not None
        assert created_event.name == "New Test Event"
        assert created_event.description == "A new test event for testing"
        assert str(created_event.creator_id) == str(test_user.id)
        assert created_event.created_at is not None
        assert created_event.updated_at is not None
    
    async def test_get_by_id(self, event_repository, test_event):
        # Act
        retrieved_event = await event_repository.get_by_id(str(test_event.id))
        
        # Assert
        assert retrieved_event is not None
        assert str(retrieved_event.id) == str(test_event.id)
        assert retrieved_event.name == test_event.name
    
    async def test_get_by_id_not_found(self, event_repository):
        # Act
        non_existent_id = str(ObjectId())
        retrieved_event = await event_repository.get_by_id(non_existent_id)
        
        # Assert
        assert retrieved_event is None
    
    async def test_get_all(self, event_repository, test_event):
        # Act
        events = await event_repository.get_all()
        
        # Assert
        assert len(events) >= 1
        assert any(str(event.id) == str(test_event.id) for event in events)
    
    async def test_get_public_events(self, event_repository, test_event):
        # Arrange
        # Make sure test_event is public
        await event_repository.update(str(test_event.id), {"is_public": True})
        
        # Create a private event
        private_event = Event(
            name="Private Event",
            description="A private event for testing",
            creator_id=test_event.creator_id,
            participants=[test_event.creator_id],
            is_public=False,
            frequency="daily"
        )
        await event_repository.create(private_event)
        
        # Act
        public_events = await event_repository.get_public_events()
        
        # Assert
        assert len(public_events) >= 1
        assert any(str(event.id) == str(test_event.id) for event in public_events)
        assert not any(event.name == "Private Event" for event in public_events)
    
    async def test_get_by_creator(self, event_repository, test_event, test_user):
        # Act
        creator_events = await event_repository.get_by_creator(str(test_user.id))
        
        # Assert
        assert len(creator_events) >= 1
        assert any(str(event.id) == str(test_event.id) for event in creator_events)
    
    async def test_get_by_participant(self, event_repository, test_event, test_user):
        # Act
        participant_events = await event_repository.get_by_participant(str(test_user.id))
        
        # Assert
        assert len(participant_events) >= 1
        assert any(str(event.id) == str(test_event.id) for event in participant_events)
    
    async def test_update(self, event_repository, test_event):
        # Arrange
        update_data = {"name": "Updated Event Name", "description": "Updated description"}
        
        # Act
        updated_event = await event_repository.update(str(test_event.id), update_data)
        
        # Assert
        assert updated_event.name == "Updated Event Name"
        assert updated_event.description == "Updated description"
        assert updated_event.updated_at > test_event.updated_at
    
    async def test_update_not_found(self, event_repository):
        # Arrange
        non_existent_id = str(ObjectId())
        update_data = {"name": "Updated Event Name"}
        
        # Act & Assert
        with pytest.raises(NotFoundException):
            await event_repository.update(non_existent_id, update_data)
    
    async def test_delete(self, event_repository, test_event):
        # Act
        result = await event_repository.delete(str(test_event.id))
        
        # Assert
        assert result is True
        deleted_event = await event_repository.get_by_id(str(test_event.id))
        assert deleted_event is None
    
    async def test_delete_not_found(self, event_repository):
        # Act
        non_existent_id = str(ObjectId())
        result = await event_repository.delete(non_existent_id)
        
        # Assert
        assert result is False
    
    async def test_add_participant(self, event_repository, test_event):
        # Arrange
        new_participant_id = str(ObjectId())
        initial_participant_count = len(test_event.participants)
        
        # Act
        updated_event = await event_repository.add_participant(str(test_event.id), new_participant_id)
        
        # Assert
        assert len(updated_event.participants) == initial_participant_count + 1
        assert ObjectId(new_participant_id) in updated_event.participants
        assert updated_event.updated_at > test_event.updated_at
    
    async def test_add_participant_already_exists(self, event_repository, test_event, test_user):
        # Act
        # Adding the same participant (test_user) again
        updated_event = await event_repository.add_participant(str(test_event.id), str(test_user.id))
        
        # Assert
        # Should not duplicate the participant
        participant_ids = [str(p) for p in updated_event.participants]
        assert participant_ids.count(str(test_user.id)) == 1
    
    async def test_add_participant_not_found(self, event_repository):
        # Act & Assert
        non_existent_id = str(ObjectId())
        with pytest.raises(NotFoundException):
            await event_repository.add_participant(non_existent_id, str(ObjectId()))
    
    async def test_remove_participant(self, event_repository, test_event, test_user):
        # Arrange
        # First, make sure the test_user is a participant
        await event_repository.add_participant(str(test_event.id), str(test_user.id))
        updated_event = await event_repository.get_by_id(str(test_event.id))
        initial_participant_count = len(updated_event.participants)
        
        # Act
        result_event = await event_repository.remove_participant(str(test_event.id), str(test_user.id))
        
        # Assert
        assert len(result_event.participants) == initial_participant_count - 1
        assert ObjectId(str(test_user.id)) not in result_event.participants
    
    async def test_remove_participant_not_found(self, event_repository):
        # Act & Assert
        non_existent_id = str(ObjectId())
        with pytest.raises(NotFoundException):
            await event_repository.remove_participant(non_existent_id, str(ObjectId()))