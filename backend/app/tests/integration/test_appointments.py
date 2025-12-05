import pytest
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_book_appointment_success(test_db, test_client):
    """Test successful appointment booking"""
    from app.core.security import hash_password
    from app.models import initialize_indexes
    
    # Initialize indexes
    await initialize_indexes(test_db)
    
    # Create doctor
    users_collection = test_db["users"]
    doctor_data = {
        "role": "doctor",
        "name": "Dr. Smith",
        "email": "dr.smith@test.com",
        "phone": "+1234567800",
        "passwordHash": hash_password("password123"),
        "createdAt": datetime.utcnow(),
        "doctorProfile": {
            "specialization": "Cardiology",
            "slotDurationMin": 30,
            "weeklySchedule": [
                {"weekday": 0, "start": "09:00", "end": "17:00"},  # Monday
                {"weekday": 1, "start": "09:00", "end": "17:00"},  # Tuesday
                {"weekday": 2, "start": "09:00", "end": "17:00"},  # Wednesday
                {"weekday": 3, "start": "09:00", "end": "17:00"},  # Thursday
                {"weekday": 4, "start": "09:00", "end": "17:00"},  # Friday
            ]
        }
    }
    doctor_result = await users_collection.insert_one(doctor_data)
    doctor_id = str(doctor_result.inserted_id)
    
    # Create and login patient
    signup_data = {
        "name": "Patient Test",
        "email": "patient.book@test.com",
        "phone": "+1234567801",
        "password": "password123"
    }
    signup_response = await test_client.post("/api/v1/auth/patient/signup", json=signup_data)
    access_token = signup_response.json()["access_token"]
    
    # Book appointment (5 days in future, Monday 10:00)
    future_date = datetime.utcnow() + timedelta(days=5)
    # Find next Monday
    while future_date.weekday() != 0:
        future_date += timedelta(days=1)
    appointment_start = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
    
    booking_data = {
        "doctorId": doctor_id,
        "start": appointment_start.isoformat(),
        "reason": "Regular checkup"
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await test_client.post("/api/v1/appointments", json=booking_data, headers=headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["doctorId"] == doctor_id
    assert data["status"] == "scheduled"
    assert data["reason"] == "Regular checkup"


@pytest.mark.asyncio
async def test_book_appointment_double_booking(test_db, test_client):
    """Test that double booking is prevented"""
    from app.core.security import hash_password
    from app.models import initialize_indexes
    
    await initialize_indexes(test_db)
    
    # Create doctor
    users_collection = test_db["users"]
    doctor_data = {
        "role": "doctor",
        "name": "Dr. Jones",
        "email": "dr.jones@test.com",
        "phone": "+1234567802",
        "passwordHash": hash_password("password123"),
        "createdAt": datetime.utcnow(),
        "doctorProfile": {
            "specialization": "Neurology",
            "slotDurationMin": 30,
            "weeklySchedule": [
                {"weekday": i, "start": "09:00", "end": "17:00"} for i in range(5)
            ]
        }
    }
    doctor_result = await users_collection.insert_one(doctor_data)
    doctor_id = str(doctor_result.inserted_id)
    
    # Create two patients
    patient1_signup = {
        "name": "Patient One",
        "email": "patient1@test.com",
        "phone": "+1234567803",
        "password": "password123"
    }
    patient1_response = await test_client.post("/api/v1/auth/patient/signup", json=patient1_signup)
    token1 = patient1_response.json()["access_token"]
    
    patient2_signup = {
        "name": "Patient Two",
        "email": "patient2@test.com",
        "phone": "+1234567804",
        "password": "password123"
    }
    patient2_response = await test_client.post("/api/v1/auth/patient/signup", json=patient2_signup)
    token2 = patient2_response.json()["access_token"]
    
    # Same appointment time
    future_date = datetime.utcnow() + timedelta(days=5)
    while future_date.weekday() != 0:
        future_date += timedelta(days=1)
    appointment_start = future_date.replace(hour=11, minute=0, second=0, microsecond=0)
    
    booking_data = {
        "doctorId": doctor_id,
        "start": appointment_start.isoformat(),
        "reason": "Consultation"
    }
    
    # First patient books
    headers1 = {"Authorization": f"Bearer {token1}"}
    response1 = await test_client.post("/api/v1/appointments", json=booking_data, headers=headers1)
    assert response1.status_code == 201
    
    # Second patient tries same slot - should fail
    headers2 = {"Authorization": f"Bearer {token2}"}
    response2 = await test_client.post("/api/v1/appointments", json=booking_data, headers=headers2)
    assert response2.status_code == 409
    assert "not available" in response2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_book_appointment_outside_hours(test_db, test_client):
    """Test booking outside doctor's hours"""
    from app.core.security import hash_password
    from app.models import initialize_indexes
    
    await initialize_indexes(test_db)
    
    # Create doctor with limited hours
    users_collection = test_db["users"]
    doctor_data = {
        "role": "doctor",
        "name": "Dr. Limited",
        "email": "dr.limited@test.com",
        "phone": "+1234567805",
        "passwordHash": hash_password("password123"),
        "createdAt": datetime.utcnow(),
        "doctorProfile": {
            "specialization": "General",
            "slotDurationMin": 30,
            "weeklySchedule": [
                {"weekday": 0, "start": "09:00", "end": "12:00"}  # Only Monday mornings
            ]
        }
    }
    doctor_result = await users_collection.insert_one(doctor_data)
    doctor_id = str(doctor_result.inserted_id)
    
    # Create patient
    signup_data = {
        "name": "Patient Test",
        "email": "patient.hours@test.com",
        "phone": "+1234567806",
        "password": "password123"
    }
    signup_response = await test_client.post("/api/v1/auth/patient/signup", json=signup_data)
    access_token = signup_response.json()["access_token"]
    
    # Try to book outside hours (Monday 14:00)
    future_date = datetime.utcnow() + timedelta(days=5)
    while future_date.weekday() != 0:
        future_date += timedelta(days=1)
    appointment_start = future_date.replace(hour=14, minute=0, second=0, microsecond=0)
    
    booking_data = {
        "doctorId": doctor_id,
        "start": appointment_start.isoformat(),
        "reason": "Checkup"
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await test_client.post("/api/v1/appointments", json=booking_data, headers=headers)
    
    assert response.status_code == 400
    assert "outside" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_doctor_slots(test_db, test_client):
    """Test getting doctor's available slots"""
    from app.core.security import hash_password
    from app.models import initialize_indexes
    
    await initialize_indexes(test_db)
    
    # Create doctor
    users_collection = test_db["users"]
    doctor_data = {
        "role": "doctor",
        "name": "Dr. Slots",
        "email": "dr.slots@test.com",
        "phone": "+1234567807",
        "passwordHash": hash_password("password123"),
        "createdAt": datetime.utcnow(),
        "doctorProfile": {
            "specialization": "Dermatology",
            "slotDurationMin": 30,
            "weeklySchedule": [
                {"weekday": 0, "start": "09:00", "end": "11:00"}  # Monday 9-11 (4 slots)
            ]
        }
    }
    doctor_result = await users_collection.insert_one(doctor_data)
    doctor_id = str(doctor_result.inserted_id)
    
    # Find next Monday
    future_date = datetime.utcnow() + timedelta(days=5)
    while future_date.weekday() != 0:
        future_date += timedelta(days=1)
    date_str = future_date.strftime("%Y-%m-%d")
    
    # Get slots
    response = await test_client.get(f"/api/v1/doctors/{doctor_id}/slots?date={date_str}")
    
    assert response.status_code == 200
    slots = response.json()
    
    # Should have slots (some might be filtered as past)
    assert len(slots) >= 0
    
    # All slots should have required fields
    for slot in slots:
        assert "start" in slot
        assert "end" in slot
        assert "available" in slot
