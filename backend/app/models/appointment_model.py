from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any, List
from datetime import datetime
from bson import ObjectId


class ReminderJobMeta(BaseModel):
    """Metadata for scheduled reminder job"""
    job_id: str
    scheduled_at: datetime


class AppointmentModel(BaseModel):
    """Appointment model for MongoDB"""
    doctorId: str = Field(..., description="Doctor's user ID")
    patientId: str = Field(..., description="Patient's user ID")
    start: datetime = Field(..., description="Appointment start time (UTC)")
    end: datetime = Field(..., description="Appointment end time (UTC)")
    status: Literal["scheduled", "confirmed", "completed", "cancelled", "no_show"] = "scheduled"
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for appointment")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    createdBy: Literal["patient", "system"] = "patient"
    reminder3hSent: bool = Field(default=False, description="Whether 3-hour reminder was sent")
    reminderJobMeta: Optional[ReminderJobMeta] = None
    twilioLogs: List[str] = Field(default_factory=list, description="Array of Twilio log IDs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "doctorId": "507f1f77bcf86cd799439011",
                "patientId": "507f1f77bcf86cd799439012",
                "start": "2025-11-20T10:00:00Z",
                "end": "2025-11-20T10:30:00Z",
                "status": "scheduled",
                "reason": "Regular checkup",
                "createdBy": "patient",
                "reminder3hSent": False
            }
        }


async def create_appointment_indexes(db):
    """Create indexes for appointments collection"""
    appointments_collection = db["appointments"]
    
    # Partial unique index on {doctorId, start} where status in ["scheduled", "confirmed"]
    # This prevents double-booking for active appointments
    await appointments_collection.create_index(
        [("doctorId", 1), ("start", 1)],
        unique=True,
        partialFilterExpression={"status": {"$in": ["scheduled", "confirmed"]}},
        name="unique_doctor_slot_active"
    )
    print("✅ Created partial unique index on appointments.{doctorId, start}")
    
    # Index on patientId + start for patient queries
    await appointments_collection.create_index(
        [("patientId", 1), ("start", -1)],
        name="patient_appointments"
    )
    print("✅ Created index on appointments.{patientId, start}")
    
    # Index on doctorId + start for doctor queries
    await appointments_collection.create_index(
        [("doctorId", 1), ("start", -1)],
        name="doctor_appointments"
    )
    print("✅ Created index on appointments.{doctorId, start}")
    
    # Index on status for filtering
    await appointments_collection.create_index("status")
    print("✅ Created index on appointments.status")
    
    # Index on start for time-based queries (reminders, no-shows)
    await appointments_collection.create_index("start")
    print("✅ Created index on appointments.start")
    
    # Compound index for no-show detection
    await appointments_collection.create_index(
        [("status", 1), ("start", 1)],
        name="no_show_detection"
    )
    print("✅ Created compound index for no-show detection")
