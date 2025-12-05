import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_twilio_webhook_confirm(test_db, test_client):
    """Test Twilio webhook CONFIRM command"""
    from app.core.security import hash_password
    from app.models import initialize_indexes
    from datetime import datetime, timedelta
    
    await initialize_indexes(test_db)
    
    # Create doctor
    users_collection = test_db["users"]
    doctor_data = {
        "role": "doctor",
        "name": "Dr. Test",
        "email": "dr.webhook@test.com",
        "phone": "+1234560000",
        "passwordHash": hash_password("password123"),
        "createdAt": datetime.utcnow(),
        "doctorProfile": {
            "specialization": "General",
            "slotDurationMin": 30,
            "weeklySchedule": [
                {"weekday": i, "start": "09:00", "end": "17:00"} for i in range(5)
            ]
        }
    }
    doctor_result = await users_collection.insert_one(doctor_data)
    doctor_id = str(doctor_result.inserted_id)
    
    # Create patient with specific phone
    patient_data = {
        "role": "patient",
        "name": "Test Patient",
        "email": "patient.webhook@test.com",
        "phone": "+1234567899",
        "passwordHash": hash_password("password123"),
        "createdAt": datetime.utcnow(),
        "patientProfile": {"age": 30, "gender": "male", "notes": None}
    }
    patient_result = await users_collection.insert_one(patient_data)
    patient_id = str(patient_result.inserted_id)
    
    # Create appointment
    appointments_collection = test_db["appointments"]
    future_start = datetime.utcnow() + timedelta(days=1)
    appointment_data = {
        "doctorId": doctor_id,
        "patientId": patient_id,
        "start": future_start,
        "end": future_start + timedelta(minutes=30),
        "status": "scheduled",
        "reason": "Test appointment",
        "createdAt": datetime.utcnow(),
        "createdBy": "patient",
        "reminder3hSent": False,
        "twilioLogs": []
    }
    apt_result = await appointments_collection.insert_one(appointment_data)
    appointment_id = str(apt_result.inserted_id)
    
    # Simulate Twilio webhook POST (CONFIRM command)
    # Note: Skipping signature verification in test
    webhook_data = {
        "From": "+1234567899",
        "To": "+1234567890",
        "Body": f"CONFIRM {appointment_id}",
        "MessageSid": "SM_test_123"
    }
    
    # Mock socket emission
    with patch('app.services.socket_service.emit_appointment_update', new_callable=AsyncMock) as mock_emit:
        # Mock Twilio send (for notification to doctor)
        with patch('app.services.twilio_service.send_sms', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"success": True, "log_id": "test_log"}
            
            response = await test_client.post("/api/v1/twilio/webhook", data=webhook_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "confirmed" in data["message"].lower()
            
            # Verify appointment was updated
            updated_apt = await appointments_collection.find_one({"_id": apt_result.inserted_id})
            assert updated_apt["status"] == "confirmed"


@pytest.mark.asyncio
async def test_twilio_webhook_cancel(test_db, test_client):
    """Test Twilio webhook CANCEL command"""
    from app.core.security import hash_password
    from app.models import initialize_indexes
    from datetime import datetime, timedelta
    
    await initialize_indexes(test_db)
    
    # Create doctor and patient
    users_collection = test_db["users"]
    doctor_data = {
        "role": "doctor",
        "name": "Dr. Cancel",
        "email": "dr.cancel@test.com",
        "phone": "+1234560001",
        "passwordHash": hash_password("password123"),
        "createdAt": datetime.utcnow(),
        "doctorProfile": {
            "specialization": "Cardiology",
            "slotDurationMin": 30,
            "weeklySchedule": [
                {"weekday": i, "start": "09:00", "end": "17:00"} for i in range(5)
            ]
        }
    }
    doctor_result = await users_collection.insert_one(doctor_data)
    doctor_id = str(doctor_result.inserted_id)
    
    patient_data = {
        "role": "patient",
        "name": "Patient Cancel",
        "email": "patient.cancel@test.com",
        "phone": "+1234567898",
        "passwordHash": hash_password("password123"),
        "createdAt": datetime.utcnow(),
        "patientProfile": {}
    }
    patient_result = await users_collection.insert_one(patient_data)
    patient_id = str(patient_result.inserted_id)
    
    # Create appointment
    appointments_collection = test_db["appointments"]
    future_start = datetime.utcnow() + timedelta(days=2)
    appointment_data = {
        "doctorId": doctor_id,
        "patientId": patient_id,
        "start": future_start,
        "end": future_start + timedelta(minutes=30),
        "status": "scheduled",
        "reason": "Cancel test",
        "createdAt": datetime.utcnow(),
        "createdBy": "patient",
        "reminder3hSent": False,
        "twilioLogs": []
    }
    apt_result = await appointments_collection.insert_one(appointment_data)
    appointment_id = str(apt_result.inserted_id)
    
    # Simulate webhook CANCEL command
    webhook_data = {
        "From": "+1234567898",
        "To": "+1234567890",
        "Body": f"CANCEL {appointment_id}",
        "MessageSid": "SM_test_456"
    }
    
    with patch('app.services.socket_service.emit_appointment_update', new_callable=AsyncMock):
        with patch('app.services.twilio_service.send_sms', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"success": True, "log_id": "test_log"}
            
            response = await test_client.post("/api/v1/twilio/webhook", data=webhook_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "cancelled" in data["message"].lower()
            
            # Verify status
            updated_apt = await appointments_collection.find_one({"_id": apt_result.inserted_id})
            assert updated_apt["status"] == "cancelled"


@pytest.mark.asyncio
async def test_twilio_webhook_invalid_command(test_client):
    """Test Twilio webhook with invalid command"""
    webhook_data = {
        "From": "+1234567890",
        "To": "+0987654321",
        "Body": "INVALID COMMAND",
        "MessageSid": "SM_test_789"
    }
    
    response = await test_client.post("/api/v1/twilio/webhook", data=webhook_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "invalid command" in data["message"].lower()
