import pytest
import pytest_asyncio
from httpx import AsyncClient
from backend.app.main import app
from app.core.db import get_database
from app.models import initialize_indexes


@pytest_asyncio.fixture
async def test_client(test_db):
    """Fixture to provide test HTTP client"""
    # Initialize indexes
    await initialize_indexes(test_db)
    
    # Override get_database to use test database
    from app.core import db as db_module
    original_db = db_module.mongodb.db
    db_module.mongodb.db = test_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Restore original database
    db_module.mongodb.db = original_db


@pytest.mark.asyncio
async def test_patient_signup(test_client):
    """Test patient signup"""
    signup_data = {
        "name": "John Doe",
        "email": "john.doe@test.com",
        "phone": "+1234567890",
        "password": "securepassword123",
        "age": 30,
        "gender": "male"
    }
    
    response = await test_client.post("/api/v1/auth/patient/signup", json=signup_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == signup_data["email"]
    assert data["user"]["role"] == "patient"
    assert "passwordHash" not in data["user"]


@pytest.mark.asyncio
async def test_patient_signup_duplicate_email(test_client):
    """Test patient signup with duplicate email"""
    signup_data = {
        "name": "John Doe",
        "email": "duplicate@test.com",
        "phone": "+1234567890",
        "password": "securepassword123"
    }
    
    # First signup should succeed
    response1 = await test_client.post("/api/v1/auth/patient/signup", json=signup_data)
    assert response1.status_code == 201
    
    # Second signup with same email should fail
    signup_data["phone"] = "+0987654321"  # Different phone
    response2 = await test_client.post("/api/v1/auth/patient/signup", json=signup_data)
    assert response2.status_code == 400
    assert "email already registered" in response2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_patient_login(test_client):
    """Test patient login"""
    # First create a patient
    signup_data = {
        "name": "Jane Doe",
        "email": "jane.doe@test.com",
        "phone": "+1234567891",
        "password": "securepassword123"
    }
    await test_client.post("/api/v1/auth/patient/signup", json=signup_data)
    
    # Now login
    login_data = {
        "email": signup_data["email"],
        "password": signup_data["password"]
    }
    response = await test_client.post("/api/v1/auth/patient/login", json=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == signup_data["email"]


@pytest.mark.asyncio
async def test_patient_login_invalid_password(test_client):
    """Test patient login with invalid password"""
    # First create a patient
    signup_data = {
        "name": "Test User",
        "email": "testuser@test.com",
        "phone": "+1234567892",
        "password": "securepassword123"
    }
    await test_client.post("/api/v1/auth/patient/signup", json=signup_data)
    
    # Try to login with wrong password
    login_data = {
        "email": signup_data["email"],
        "password": "wrongpassword"
    }
    response = await test_client.post("/api/v1/auth/patient/login", json=login_data)
    
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_doctor_login(test_db, test_client):
    """Test doctor login with seeded account"""
    from app.core.security import hash_password
    from datetime import datetime
    
    # Create a doctor account (simulating seed)
    users_collection = test_db["users"]
    doctor_data = {
        "role": "doctor",
        "name": "Dr. Smith",
        "email": "dr.smith@clinic.com",
        "phone": "+1234567893",
        "passwordHash": hash_password("doctorpassword123"),
        "createdAt": datetime.utcnow(),
        "doctorProfile": {
            "specialization": "Cardiology",
            "slotDurationMin": 30,
            "weeklySchedule": [
                {"weekday": 0, "start": "09:00", "end": "17:00"}
            ]
        }
    }
    await users_collection.insert_one(doctor_data)
    
    # Login as doctor
    login_data = {
        "email": "dr.smith@clinic.com",
        "password": "doctorpassword123"
    }
    response = await test_client.post("/api/v1/auth/doctor/login", json=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "doctor"
    assert data["user"]["doctorProfile"]["specialization"] == "Cardiology"


@pytest.mark.asyncio
async def test_doctor_cannot_login_as_patient(test_db, test_client):
    """Test that doctor cannot login via patient endpoint"""
    from app.core.security import hash_password
    from datetime import datetime
    
    # Create a doctor account
    users_collection = test_db["users"]
    doctor_data = {
        "role": "doctor",
        "name": "Dr. Jones",
        "email": "dr.jones@clinic.com",
        "phone": "+1234567894",
        "passwordHash": hash_password("doctorpassword123"),
        "createdAt": datetime.utcnow(),
        "doctorProfile": {
            "specialization": "Neurology",
            "slotDurationMin": 30,
            "weeklySchedule": []
        }
    }
    await users_collection.insert_one(doctor_data)
    
    # Try to login as patient
    login_data = {
        "email": "dr.jones@clinic.com",
        "password": "doctorpassword123"
    }
    response = await test_client.post("/api/v1/auth/patient/login", json=login_data)
    
    assert response.status_code == 403
    assert "only patients" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_refresh_token(test_client):
    """Test refresh token functionality"""
    # Create and login a patient
    signup_data = {
        "name": "Refresh Test",
        "email": "refresh@test.com",
        "phone": "+1234567895",
        "password": "securepassword123"
    }
    signup_response = await test_client.post("/api/v1/auth/patient/signup", json=signup_data)
    refresh_token = signup_response.json()["refresh_token"]
    
    # Use refresh token to get new access token
    refresh_data = {"refresh_token": refresh_token}
    response = await test_client.post("/api/v1/auth/refresh", json=refresh_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_current_user(test_client):
    """Test getting current user profile"""
    # Signup and get token
    signup_data = {
        "name": "Profile Test",
        "email": "profile@test.com",
        "phone": "+1234567896",
        "password": "securepassword123"
    }
    signup_response = await test_client.post("/api/v1/auth/patient/signup", json=signup_data)
    access_token = signup_response.json()["access_token"]
    
    # Get profile
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await test_client.get("/api/v1/users/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == signup_data["email"]
    assert data["name"] == signup_data["name"]


@pytest.mark.asyncio
async def test_update_patient_profile(test_client):
    """Test updating patient profile"""
    # Signup and get token
    signup_data = {
        "name": "Update Test",
        "email": "update@test.com",
        "phone": "+1234567897",
        "password": "securepassword123",
        "age": 25
    }
    signup_response = await test_client.post("/api/v1/auth/patient/signup", json=signup_data)
    access_token = signup_response.json()["access_token"]
    
    # Update profile
    update_data = {
        "name": "Updated Name",
        "age": 26,
        "gender": "female"
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await test_client.patch("/api/v1/users/me", json=update_data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["patientProfile"]["age"] == 26
    assert data["patientProfile"]["gender"] == "female"
