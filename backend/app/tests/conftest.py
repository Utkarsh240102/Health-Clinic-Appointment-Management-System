import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


@pytest_asyncio.fixture
async def test_db():
    """Fixture to provide a test database"""
    # Use a separate test database
    test_db_name = f"{settings.MONGODB_DB_NAME}_test"
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[test_db_name]
    
    yield db
    
    # Cleanup: drop test database after tests
    await client.drop_database(test_db_name)
    client.close()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "doctor": {
            "role": "doctor",
            "name": "Dr. John Smith",
            "email": "john.smith@test.com",
            "phone": "+1234567890",
            "passwordHash": "hashed_password",
            "doctorProfile": {
                "specialization": "Cardiology",
                "slotDurationMin": 30,
                "weeklySchedule": [
                    {"weekday": 0, "start": "09:00", "end": "17:00"},
                    {"weekday": 2, "start": "09:00", "end": "17:00"}
                ]
            }
        },
        "patient": {
            "role": "patient",
            "name": "Jane Doe",
            "email": "jane.doe@test.com",
            "phone": "+0987654321",
            "passwordHash": "hashed_password",
            "patientProfile": {
                "age": 30,
                "gender": "female",
                "notes": "No known allergies"
            }
        }
    }
