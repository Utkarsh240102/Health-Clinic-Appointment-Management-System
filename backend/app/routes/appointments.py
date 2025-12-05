from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.appointment import (
    CreateAppointmentRequest,
    AppointmentResponse,
    SlotResponse,
    DoctorStatsResponse
)
from app.services.appointment_service import (
    create_appointment,
    get_appointments,
    get_appointment_by_id,
    update_appointment_status,
    get_doctor_stats,
    get_doctor_slots
)
from app.core.security import get_current_user, get_current_patient, get_current_doctor
from typing import Dict, Any, List, Optional

router = APIRouter()


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def book_appointment(
    request: CreateAppointmentRequest,
    current_user: Dict[str, Any] = Depends(get_current_patient)
):
    """
    Book a new appointment (patient only)
    
    - Validates doctor availability
    - Validates slot alignment
    - Prevents double-booking via unique index
    - Schedules 3-hour reminder if applicable
    """
    appointment = await create_appointment(
        doctor_id=request.doctorId,
        patient_id=current_user["_id"],
        start=request.start,
        reason=request.reason
    )
    
    return appointment


@router.get("", response_model=List[AppointmentResponse])
async def list_appointments(
    role: str = Query(..., description="Filter by role: doctor or patient"),
    limit: int = Query(10, ge=1, le=100),
    month: Optional[str] = Query(None, description="Filter by month: YYYY-MM"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List appointments for current user
    
    - Returns recent appointments (default 10)
    - Can filter by month
    - Role determines which appointments are returned
    """
    # Validate role matches user
    if role != current_user["role"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role mismatch: user is {current_user['role']}, requested {role}"
        )
    
    appointments = await get_appointments(
        role=role,
        user_id=current_user["_id"],
        limit=limit,
        month=month
    )
    
    return appointments


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get appointment details
    
    - Returns appointment if user is doctor or patient for this appointment
    """
    appointment = await get_appointment_by_id(appointment_id)
    
    # Verify user has access to this appointment - compare ObjectIds as strings
    user_id = current_user["_id"]
    if str(appointment["doctorId"]) != user_id and str(appointment["patientId"]) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this appointment"
        )
    
    return appointment


@router.patch("/{appointment_id}/confirm", response_model=AppointmentResponse)
async def confirm_appointment(
    appointment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_patient)
):
    """
    Confirm appointment (patient only)
    
    - Typically triggered by 3-hour reminder
    - Can be done up to appointment start time
    """
    updated = await update_appointment_status(
        appointment_id=appointment_id,
        new_status="confirmed",
        user_id=current_user["_id"],
        user_role=current_user["role"]
    )
    
    return updated


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_patient)
):
    """
    Cancel appointment (patient only)
    
    - Patient can cancel their own appointments
    - Cannot cancel completed or no-show appointments
    """
    updated = await update_appointment_status(
        appointment_id=appointment_id,
        new_status="cancelled",
        user_id=current_user["_id"],
        user_role=current_user["role"]
    )
    
    return updated


@router.patch("/{appointment_id}/complete", response_model=AppointmentResponse)
async def complete_appointment(
    appointment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_doctor)
):
    """
    Mark appointment as completed (doctor only)
    
    - Only doctors can mark appointments as completed
    - Typically done from "Today's Schedule" page
    """
    updated = await update_appointment_status(
        appointment_id=appointment_id,
        new_status="completed",
        user_id=current_user["_id"],
        user_role=current_user["role"]
    )
    
    return updated


@router.get("/stats/doctor/{doctor_id}", response_model=DoctorStatsResponse)
async def get_doctor_appointment_stats(
    doctor_id: str,
    groupBy: str = Query("month", description="Group by: month or day"),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get appointment statistics for a doctor
    
    - Returns aggregated data grouped by month or day
    - Includes counts by status
    - Limited to specified number of periods
    """
    stats = await get_doctor_stats(doctor_id, group_by=groupBy, limit=limit)
    return stats


@router.get("/slots/{doctor_id}", response_model=List[SlotResponse])
async def get_available_slots(
    doctor_id: str,
    date: str = Query(..., description="Date in YYYY-MM-DD format")
):
    """
    Get available time slots for a doctor on a specific date
    
    - Returns all slots with availability status
    - Shows booked and available slots
    - Public endpoint for appointment booking UI
    """
    slots = await get_doctor_slots(doctor_id, date)
    return slots
