import pytest
import pytest_asyncio
from app.models.user_model import create_user_indexes
from app.models.appointment_model import create_appointment_indexes
from app.models.twilio_log_model import create_twilio_log_indexes


@pytest_asyncio.fixture
async def db_with_indexes(test_db):
    """Fixture to provide database with indexes created"""
    await create_user_indexes(test_db)
    await create_appointment_indexes(test_db)
    await create_twilio_log_indexes(test_db)
    return test_db


@pytest.mark.asyncio
async def test_user_indexes_created(db_with_indexes):
    """Test that user indexes are created correctly"""
    users_collection = db_with_indexes["users"]
    indexes = await users_collection.index_information()
    
    # Check email unique index exists
    assert "email_1" in indexes
    assert indexes["email_1"]["unique"] is True
    
    # Check phone unique index exists
    assert "phone_1" in indexes
    assert indexes["phone_1"]["unique"] is True
    
    # Check role index exists
    assert "role_1" in indexes


@pytest.mark.asyncio
async def test_appointment_indexes_created(db_with_indexes):
    """Test that appointment indexes are created correctly"""
    appointments_collection = db_with_indexes["appointments"]
    indexes = await appointments_collection.index_information()
    
    # Check partial unique index exists
    assert "unique_doctor_slot_active" in indexes
    assert indexes["unique_doctor_slot_active"]["unique"] is True
    assert "partialFilterExpression" in indexes["unique_doctor_slot_active"]
    
    # Check patient appointments index exists
    assert "patient_appointments" in indexes
    
    # Check doctor appointments index exists
    assert "doctor_appointments" in indexes
    
    # Check status index exists
    assert "status_1" in indexes
    
    # Check start index exists
    assert "start_1" in indexes
    
    # Check no-show detection index exists
    assert "no_show_detection" in indexes


@pytest.mark.asyncio
async def test_twilio_log_indexes_created(db_with_indexes):
    """Test that twilio_logs indexes are created correctly"""
    twilio_logs_collection = db_with_indexes["twilio_logs"]
    indexes = await twilio_logs_collection.index_information()
    
    # Check appointmentId index exists
    assert "appointmentId_1" in indexes
    
    # Check timestamp index exists
    assert "timestamp_-1" in indexes
    
    # Check twilioSid index exists
    assert "twilioSid_1" in indexes
    assert indexes["twilioSid_1"].get("sparse") is True
    
    # Check direction index exists
    assert "direction_1" in indexes


@pytest.mark.asyncio
async def test_partial_unique_index_enforcement(db_with_indexes):
    """Test that partial unique index prevents double-booking"""
    from datetime import datetime, timedelta
    
    appointments_collection = db_with_indexes["appointments"]
    
    # Insert first appointment with status "scheduled"
    appointment1 = {
        "doctorId": "doctor123",
        "patientId": "patient123",
        "start": datetime.utcnow() + timedelta(hours=5),
        "end": datetime.utcnow() + timedelta(hours=5, minutes=30),
        "status": "scheduled",
        "reason": "Checkup",
        "createdAt": datetime.utcnow(),
        "createdBy": "patient",
        "reminder3hSent": False,
        "twilioLogs": []
    }
    result1 = await appointments_collection.insert_one(appointment1)
    assert result1.inserted_id is not None
    
    # Try to insert duplicate appointment with same doctor and start time
    appointment2 = appointment1.copy()
    appointment2["patientId"] = "patient456"  # Different patient
    
    # This should fail due to unique index
    with pytest.raises(Exception) as exc_info:
        await appointments_collection.insert_one(appointment2)
    
    # Check that it's a duplicate key error
    assert "duplicate key error" in str(exc_info.value).lower() or "E11000" in str(exc_info.value)
    
    # Now mark first appointment as cancelled - should allow same slot
    await appointments_collection.update_one(
        {"_id": result1.inserted_id},
        {"$set": {"status": "cancelled"}}
    )
    
    # Now inserting appointment2 should work (cancelled appointments don't block)
    appointment3 = appointment1.copy()
    appointment3["patientId"] = "patient789"
    appointment3["status"] = "scheduled"
    result3 = await appointments_collection.insert_one(appointment3)
    assert result3.inserted_id is not None


@pytest.mark.asyncio
async def test_user_email_uniqueness(db_with_indexes):
    """Test that email uniqueness is enforced"""
    from app.models.user_model import UserModel
    from datetime import datetime
    
    users_collection = db_with_indexes["users"]
    
    # Insert first user
    user1_data = {
        "role": "patient",
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+1234567890",
        "passwordHash": "hashed",
        "createdAt": datetime.utcnow()
    }
    result1 = await users_collection.insert_one(user1_data)
    assert result1.inserted_id is not None
    
    # Try to insert user with same email
    user2_data = user1_data.copy()
    user2_data["phone"] = "+0987654321"  # Different phone
    
    with pytest.raises(Exception) as exc_info:
        await users_collection.insert_one(user2_data)
    
    assert "duplicate key error" in str(exc_info.value).lower() or "E11000" in str(exc_info.value)
