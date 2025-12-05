import pytest
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_get_doctor_stats(test_db, test_client):
    """Test doctor statistics aggregation"""
    from app.core.security import hash_password
    from app.models import initialize_indexes
    
    await initialize_indexes(test_db)
    
    # Create doctor
    users_collection = test_db["users"]
    doctor_data = {
        "role": "doctor",
        "name": "Dr. Stats",
        "email": "dr.stats@test.com",
        "phone": "+1234560010",
        "passwordHash": hash_password("password123"),
        "createdAt": datetime.utcnow(),
        "doctorProfile": {
            "specialization": "Cardiology",
            "slotDurationMin": 30,
            "weeklySchedule": []
        }
    }
    doctor_result = await users_collection.insert_one(doctor_data)
    doctor_id = str(doctor_result.inserted_id)
    
    # Create patient
    patient_data = {
        "role": "patient",
        "name": "Patient Stats",
        "email": "patient.stats@test.com",
        "phone": "+1234560011",
        "passwordHash": hash_password("password123"),
        "createdAt": datetime.utcnow(),
        "patientProfile": {}
    }
    patient_result = await users_collection.insert_one(patient_data)
    patient_id = str(patient_result.inserted_id)
    
    # Create several appointments with different statuses
    appointments_collection = test_db["appointments"]
    base_date = datetime(2025, 11, 1, 10, 0)
    
    appointments = [
        {"status": "completed", "days_offset": 0},
        {"status": "completed", "days_offset": 1},
        {"status": "cancelled", "days_offset": 2},
        {"status": "no_show", "days_offset": 3},
        {"status": "scheduled", "days_offset": 30},  # Next month
    ]
    
    for apt in appointments:
        apt_date = base_date + timedelta(days=apt["days_offset"])
        apt_doc = {
            "doctorId": doctor_id,
            "patientId": patient_id,
            "start": apt_date,
            "end": apt_date + timedelta(minutes=30),
            "status": apt["status"],
            "reason": "Test",
            "createdAt": datetime.utcnow(),
            "createdBy": "patient",
            "reminder3hSent": False,
            "twilioLogs": []
        }
        await appointments_collection.insert_one(apt_doc)
    
    # Get stats
    response = await test_client.get(f"/api/v1/appointments/stats/doctor/{doctor_id}?groupBy=month&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    assert data["doctorId"] == doctor_id
    assert data["totalAppointments"] == 5
    assert len(data["stats"]) > 0
    
    # Check first period (should be most recent)
    first_stat = data["stats"][0]
    assert "period" in first_stat
    assert "count" in first_stat
    assert "completed" in first_stat


@pytest.mark.asyncio
async def test_get_server_time(test_client):
    """Test server time endpoint"""
    response = await test_client.get("/api/v1/time/now")
    
    assert response.status_code == 200
    data = response.json()
    assert "server_utc" in data
    
    # Verify it's a valid ISO datetime
    server_time = data["server_utc"]
    assert "T" in server_time
    assert server_time.endswith("Z")
    
    # Parse to ensure valid
    from datetime import datetime
    parsed = datetime.fromisoformat(server_time.replace("Z", "+00:00"))
    assert parsed is not None
