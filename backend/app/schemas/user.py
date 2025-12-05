from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal, List
from datetime import datetime


class WeeklyScheduleResponse(BaseModel):
    """Weekly schedule response"""
    weekday: int
    start: str
    end: str


class DoctorProfileResponse(BaseModel):
    """Doctor profile response"""
    specialization: str
    slotDurationMin: int
    weeklySchedule: List[WeeklyScheduleResponse]
    explicitSlots: Optional[List[datetime]] = None


class PatientProfileResponse(BaseModel):
    """Patient profile response"""
    age: Optional[int] = None
    gender: Optional[str] = None
    notes: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema"""
    id: str = Field(..., alias="_id")
    role: Literal["doctor", "patient"]
    name: str
    email: EmailStr
    phone: str
    photoUrl: Optional[str] = None
    createdAt: datetime
    doctorProfile: Optional[DoctorProfileResponse] = None
    patientProfile: Optional[PatientProfileResponse] = None
    
    class Config:
        populate_by_name = True


class UpdateUserRequest(BaseModel):
    """Update user request (patient only)"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    phone: Optional[str] = Field(default=None, pattern=r"^\+?[1-9]\d{1,14}$")
    age: Optional[int] = Field(default=None, ge=0, le=150)
    gender: Optional[str] = None
    notes: Optional[str] = None
