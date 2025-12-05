from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import datetime


class WeeklyScheduleSlot(BaseModel):
    """Weekly schedule slot for a doctor"""
    weekday: int = Field(..., ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    start: str = Field(..., pattern=r"^([01]\d|2[0-3]):([0-5]\d)$", description="Start time HH:MM")
    end: str = Field(..., pattern=r"^([01]\d|2[0-3]):([0-5]\d)$", description="End time HH:MM")


class DoctorProfile(BaseModel):
    """Doctor-specific profile data"""
    specialization: str
    slotDurationMin: int = Field(default=30, description="Slot duration in minutes")
    weeklySchedule: List[WeeklyScheduleSlot] = Field(default_factory=list)
    explicitSlots: Optional[List[datetime]] = Field(default=None, description="Specific available datetime slots")


class PatientProfile(BaseModel):
    """Patient-specific profile data"""
    age: Optional[int] = Field(default=None, ge=0, le=150)
    gender: Optional[Literal["male", "female", "other"]] = None
    notes: Optional[str] = None


class UserModel(BaseModel):
    """User model for MongoDB"""
    role: Literal["doctor", "patient"]
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$")
    passwordHash: str
    photoUrl: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    doctorProfile: Optional[DoctorProfile] = None
    patientProfile: Optional[PatientProfile] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "doctor",
                "name": "Dr. John Smith",
                "email": "john.smith@clinic.com",
                "phone": "+1234567890",
                "passwordHash": "hashed_password_here",
                "photoUrl": "https://example.com/photo.jpg",
                "doctorProfile": {
                    "specialization": "Cardiology",
                    "slotDurationMin": 30,
                    "weeklySchedule": [
                        {"weekday": 0, "start": "09:00", "end": "17:00"},
                        {"weekday": 2, "start": "09:00", "end": "17:00"}
                    ]
                }
            }
        }


async def create_user_indexes(db):
    """Create indexes for users collection"""
    users_collection = db["users"]
    
    # Unique index on email
    await users_collection.create_index("email", unique=True)
    print("✅ Created unique index on users.email")
    
    # Unique index on phone
    await users_collection.create_index("phone", unique=True)
    print("✅ Created unique index on users.phone")
    
    # Index on role for filtering
    await users_collection.create_index("role")
    print("✅ Created index on users.role")
