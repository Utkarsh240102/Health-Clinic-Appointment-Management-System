from fastapi import HTTPException, status
from app.core.db import get_appointments_collection, get_users_collection
from app.utils.availability import validate_appointment_slot, generate_slots_for_day, filter_past_slots
from app.utils.time_utils import utc_now, ensure_utc
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument
from typing import Dict, Any, List, Optional


async def get_doctor_by_id(doctor_id: str) -> Dict[str, Any]:
    """Get doctor by ID"""
    users_collection = get_users_collection()
    
    try:
        doctor = await users_collection.find_one({
            "_id": ObjectId(doctor_id),
            "role": "doctor"
        })
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid doctor ID"
        )
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    return doctor


async def create_appointment(
    doctor_id: str,
    patient_id: str,
    start: datetime,
    reason: str
) -> Dict[str, Any]:
    """Create a new appointment with validation"""
    appointments_collection = get_appointments_collection()
    
    # Ensure start time is in UTC (naive datetime)
    start = ensure_utc(start)
    now = utc_now()
    
    # Get doctor profile
    doctor = await get_doctor_by_id(doctor_id)
    doctor_profile = doctor.get("doctorProfile", {})
    
    # Validate slot (both should be naive UTC)
    is_valid, error_msg = validate_appointment_slot(start, doctor_profile, now)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Calculate end time (30 minutes)
    slot_duration = doctor_profile.get("slotDurationMin", 30)
    end = start + timedelta(minutes=slot_duration)
    
    # Create appointment document
    appointment_doc = {
        "doctorId": ObjectId(doctor_id),  # Store as ObjectId for proper joins
        "patientId": ObjectId(patient_id),  # Store as ObjectId for proper joins
        "start": start.replace(tzinfo=None),  # Store as naive UTC
        "end": end.replace(tzinfo=None),
        "status": "scheduled",
        "reason": reason,
        "createdAt": now.replace(tzinfo=None),
        "createdBy": "patient",
        "reminder3hSent": False,
        "twilioLogs": []
    }
    
    # Try to insert (will fail if slot taken due to unique index)
    try:
        result = await appointments_collection.insert_one(appointment_doc)
        
        # Convert ObjectIds to strings for JSON serialization
        appointment_doc["_id"] = str(result.inserted_id)
        appointment_doc["doctorId"] = str(appointment_doc["doctorId"])
        appointment_doc["patientId"] = str(appointment_doc["patientId"])
        
        # Schedule reminder job if appointment is more than 3 hours away
        reminder_time = start - timedelta(hours=3)
        if reminder_time > now:
            from app.services.scheduler_service import schedule_reminder_job
            job_meta = await schedule_reminder_job(str(result.inserted_id), reminder_time.replace(tzinfo=None))
            
            # Update appointment with job metadata
            if job_meta:
                await appointments_collection.update_one(
                    {"_id": result.inserted_id},
                    {"$set": {"reminderJobMeta": job_meta}}
                )
                appointment_doc["reminderJobMeta"] = job_meta
        
        return appointment_doc
        
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Slot not available - doctor already has an appointment at this time"
        )


async def get_appointments(
    role: str,
    user_id: str,
    limit: int = 10,
    month: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get appointments for user (patient or doctor)"""
    appointments_collection = get_appointments_collection()
    
    # Build query - convert string ID to ObjectId for proper matching
    if role == "doctor":
        query = {"doctorId": ObjectId(user_id)}
    else:
        query = {"patientId": ObjectId(user_id)}
    
    # Add month filter if provided
    if month:
        try:
            year, month_num = month.split("-")
            start_date = datetime(int(year), int(month_num), 1)
            if int(month_num) == 12:
                end_date = datetime(int(year) + 1, 1, 1)
            else:
                end_date = datetime(int(year), int(month_num) + 1, 1)
            
            query["start"] = {"$gte": start_date, "$lt": end_date}
        except (ValueError, IndexError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid month format. Use YYYY-MM"
            )
    
    # Fetch appointments
    cursor = appointments_collection.find(query).sort("start", -1).limit(limit)
    appointments = await cursor.to_list(length=limit)
    
    # Convert ObjectIds to strings for JSON serialization
    for apt in appointments:
        apt["_id"] = str(apt["_id"])
        apt["doctorId"] = str(apt["doctorId"])
        apt["patientId"] = str(apt["patientId"])
    
    return appointments


async def get_appointment_by_id(appointment_id: str) -> Dict[str, Any]:
    """Get appointment by ID"""
    appointments_collection = get_appointments_collection()
    
    try:
        appointment = await appointments_collection.find_one({"_id": ObjectId(appointment_id)})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid appointment ID"
        )
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Convert ObjectIds to strings for JSON serialization
    appointment["_id"] = str(appointment["_id"])
    appointment["doctorId"] = str(appointment["doctorId"])
    appointment["patientId"] = str(appointment["patientId"])
    return appointment


async def update_appointment_status(
    appointment_id: str,
    new_status: str,
    user_id: str,
    user_role: str
) -> Dict[str, Any]:
    """Update appointment status"""
    appointments_collection = get_appointments_collection()
    
    # Get appointment
    appointment = await get_appointment_by_id(appointment_id)
    
    # Validate permissions - compare ObjectIds
    if user_role == "patient" and str(appointment["patientId"]) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own appointments"
        )
    
    if user_role == "doctor" and str(appointment["doctorId"]) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own appointments"
        )
    
    # Validate status transitions
    current_status = appointment["status"]
    
    if new_status == "confirmed" and current_status not in ["scheduled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only confirm scheduled appointments"
        )
    
    if new_status == "cancelled" and current_status in ["completed", "no_show"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed or no-show appointments"
        )
    
    if new_status == "completed" and user_role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can mark appointments as completed"
        )
    
    # Update status
    updated = await appointments_collection.find_one_and_update(
        {"_id": ObjectId(appointment_id)},
        {"$set": {"status": new_status}},
        return_document=ReturnDocument.AFTER
    )
    
    # Send notifications
    if new_status == "confirmed":
        from app.services.twilio_service import send_confirmation_notification
        await send_confirmation_notification(updated)
    elif new_status == "cancelled":
        from app.services.twilio_service import send_cancellation_notification
        await send_cancellation_notification(updated)
    
    # Convert ObjectIds to strings for JSON serialization
    updated["_id"] = str(updated["_id"])
    updated["doctorId"] = str(updated["doctorId"])
    updated["patientId"] = str(updated["patientId"])
    return updated


async def get_doctor_slots(doctor_id: str, date_str: str) -> List[Dict[str, Any]]:
    """Get available and taken slots for a doctor on a specific date"""
    # Parse date
    try:
        date = datetime.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Get doctor
    doctor = await get_doctor_by_id(doctor_id)
    doctor_profile = doctor.get("doctorProfile", {})
    
    # Generate all possible slots for the day
    all_slots = generate_slots_for_day(date, doctor_profile)
    
    # Filter past slots
    all_slots = filter_past_slots(all_slots, utc_now().replace(tzinfo=None))
    
    # Get booked appointments for this date
    appointments_collection = get_appointments_collection()
    start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    booked = await appointments_collection.find({
        "doctorId": ObjectId(doctor_id),  # Use ObjectId for proper matching
        "start": {"$gte": start_of_day, "$lt": end_of_day},
        "status": {"$in": ["scheduled", "confirmed"]}
    }).to_list(length=None)
    
    booked_starts = {apt["start"] for apt in booked}
    appointment_map = {apt["start"]: str(apt["_id"]) for apt in booked}
    
    # Mark slots as available or not
    result = []
    for slot in all_slots:
        is_available = slot["start"] not in booked_starts
        result.append({
            "start": slot["start"],
            "end": slot["end"],
            "available": is_available,
            "appointmentId": appointment_map.get(slot["start"])
        })
    
    return result


async def get_doctor_stats(
    doctor_id: str,
    group_by: str = "month",
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get doctor appointment statistics with aggregation
    
    Groups appointments by specified period (month or day)
    Returns counts by status
    """
    appointments_collection = get_appointments_collection()
    
    # Verify doctor exists
    await get_doctor_by_id(doctor_id)
    
    # Build aggregation pipeline
    if group_by == "month":
        group_format = "%Y-%m"
    elif group_by == "day":
        group_format = "%Y-%m-%d"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid groupBy parameter. Use 'month' or 'day'"
        )
    
    pipeline = [
        # Match appointments for this doctor - use ObjectId
        {"$match": {"doctorId": ObjectId(doctor_id)}},
        
        # Add period field
        {
            "$addFields": {
                "period": {
                    "$dateToString": {
                        "format": group_format,
                        "date": "$start"
                    }
                }
            }
        },
        
        # Group by period
        {
            "$group": {
                "_id": "$period",
                "total": {"$sum": 1},
                "completed": {
                    "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                },
                "cancelled": {
                    "$sum": {"$cond": [{"$eq": ["$status", "cancelled"]}, 1, 0]}
                },
                "no_show": {
                    "$sum": {"$cond": [{"$eq": ["$status", "no_show"]}, 1, 0]}
                },
                "scheduled": {
                    "$sum": {"$cond": [{"$eq": ["$status", "scheduled"]}, 1, 0]}
                },
                "confirmed": {
                    "$sum": {"$cond": [{"$eq": ["$status", "confirmed"]}, 1, 0]}
                }
            }
        },
        
        # Sort by period descending
        {"$sort": {"_id": -1}},
        
        # Limit results
        {"$limit": limit},
        
        # Project to desired format
        {
            "$project": {
                "_id": 0,
                "period": "$_id",
                "count": "$total",
                "completed": 1,
                "cancelled": 1,
                "no_show": 1,
                "scheduled": 1,
                "confirmed": 1
            }
        }
    ]
    
    # Execute aggregation
    cursor = appointments_collection.aggregate(pipeline)
    stats = await cursor.to_list(length=limit)
    
    # Get total count - use ObjectId
    total_count = await appointments_collection.count_documents({"doctorId": ObjectId(doctor_id)})
    
    return {
        "doctorId": doctor_id,
        "totalAppointments": total_count,
        "stats": stats
    }

