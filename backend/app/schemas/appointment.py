from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class CreateAppointmentRequest(BaseModel):
    """Create appointment request"""
    doctorId: str = Field(..., min_length=24, max_length=24)
    start: datetime
    reason: str = Field(..., min_length=1, max_length=500)


class AppointmentResponse(BaseModel):
    """Appointment response schema"""
    id: str = Field(..., alias="_id")
    doctorId: str
    patientId: str
    start: datetime
    end: datetime
    status: Literal["scheduled", "confirmed", "completed", "cancelled", "no_show"]
    reason: str
    createdAt: datetime
    createdBy: Literal["patient", "system"]
    reminder3hSent: bool
    reminderJobMeta: Optional[dict] = None
    
    class Config:
        populate_by_name = True


class SlotResponse(BaseModel):
    """Slot availability response"""
    start: datetime
    end: datetime
    available: bool
    appointmentId: Optional[str] = None


class StatsGroupItem(BaseModel):
    """Statistics group item"""
    period: str  # e.g., "2025-11" for month grouping
    count: int
    completed: int
    cancelled: int
    no_show: int


class DoctorStatsResponse(BaseModel):
    """Doctor statistics response"""
    doctorId: str
    totalAppointments: int
    stats: list[StatsGroupItem]
