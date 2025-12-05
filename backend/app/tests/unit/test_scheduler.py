import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_twilio_service_send_sms_mock():
    """Test Twilio SMS sending with mock"""
    from app.services.twilio_service import send_sms
    
    with patch('app.services.twilio_service.twilio_client') as mock_client:
        # Mock Twilio response
        mock_message = Mock()
        mock_message.sid = "SM1234567890"
        mock_message.status = "sent"
        mock_client.messages.create.return_value = mock_message
        
        # Send SMS
        result = await send_sms(
            to="+1234567890",
            body="Test message",
            from_number="+0987654321",
            appointment_id="test123"
        )
        
        assert result["success"] is True
        assert result["sid"] == "SM1234567890"
        assert "log_id" in result
        
        # Verify Twilio client was called
        mock_client.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_schedule_reminder_job():
    """Test scheduling a reminder job"""
    from app.services.scheduler_service import schedule_reminder_job
    from backend.app.main import get_scheduler
    
    scheduler = get_scheduler()
    
    # Schedule a job
    appointment_id = "test_apt_123"
    reminder_time = datetime.utcnow() + timedelta(hours=1)
    
    job_meta = await schedule_reminder_job(appointment_id, reminder_time)
    
    assert job_meta is not None
    assert "job_id" in job_meta
    assert "scheduled_at" in job_meta
    assert job_meta["job_id"] == f"reminder_{appointment_id}"
    
    # Check job exists in scheduler
    job = scheduler.get_job(f"reminder_{appointment_id}")
    assert job is not None
    
    # Clean up
    scheduler.remove_job(f"reminder_{appointment_id}")


@pytest.mark.asyncio
async def test_auto_cancel_no_shows_function(test_db):
    """Test the auto-cancel no-shows function"""
    from app.services.scheduler_service import auto_cancel_no_shows
    from app.models import initialize_indexes
    
    await initialize_indexes(test_db)
    
    # Create a past appointment that should be marked no-show
    appointments_collection = test_db["appointments"]
    past_start = datetime.utcnow() - timedelta(minutes=20)
    
    appointment_doc = {
        "doctorId": "doctor123",
        "patientId": "patient123",
        "start": past_start,
        "end": past_start + timedelta(minutes=30),
        "status": "scheduled",
        "reason": "Test appointment",
        "createdAt": datetime.utcnow(),
        "createdBy": "patient",
        "reminder3hSent": False,
        "twilioLogs": []
    }
    
    result = await appointments_collection.insert_one(appointment_doc)
    appointment_id = result.inserted_id
    
    # Mock Twilio send to avoid actual SMS
    with patch('app.services.twilio_service.send_sms', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = {"success": True, "log_id": "mock_log"}
        
        # Run auto-cancel function
        await auto_cancel_no_shows()
        
        # Check appointment was marked no-show
        updated_apt = await appointments_collection.find_one({"_id": appointment_id})
        assert updated_apt["status"] == "no_show"
