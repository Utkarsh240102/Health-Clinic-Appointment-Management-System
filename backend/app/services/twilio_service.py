"""
Twilio service for sending SMS messages and logging
"""
from twilio.rest import Client
from app.config import settings
from app.core.db import get_twilio_logs_collection, get_users_collection
from datetime import datetime
from bson import ObjectId
from typing import Dict, Any


# Initialize Twilio client
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


async def log_twilio_message(
    to: str,
    from_: str,
    body: str,
    status: str,
    direction: str,
    appointment_id: str = None,
    twilio_sid: str = None,
    error_code: str = None,
    error_message: str = None
) -> str:
    """Log Twilio message to database"""
    twilio_logs_collection = get_twilio_logs_collection()
    
    log_doc = {
        "to": to,
        "from": from_,
        "body": body,
        "status": status,
        "timestamp": datetime.utcnow(),
        "direction": direction,
        "appointmentId": appointment_id,
        "twilioSid": twilio_sid,
        "errorCode": error_code,
        "errorMessage": error_message
    }
    
    result = await twilio_logs_collection.insert_one(log_doc)
    return str(result.inserted_id)


async def send_sms(to: str, body: str, from_number: str = None, appointment_id: str = None) -> Dict[str, Any]:
    """
    Send SMS via Twilio with retry and logging
    Smart filtering: Skip fake test numbers (+1555*) but send to real numbers
    """
    if from_number is None:
        from_number = settings.TWILIO_FROM_PATIENT
    
    # Skip fake seeded test numbers to avoid Twilio errors
    if to.startswith("+1555"):
        print(f"⏭️ Skipping SMS to test number: {to}")
        log_id = await log_twilio_message(
            to=to,
            from_=from_number,
            body=body,
            status="skipped",
            direction="outbound",
            appointment_id=appointment_id,
            error_message="Test number - not sent"
        )
        return {
            "success": True,
            "skipped": True,
            "log_id": log_id
        }
    
    try:
        # Send message to real numbers only
        message = twilio_client.messages.create(
            to=to,
            from_=from_number,
            body=body
        )
        
        # Log message
        log_id = await log_twilio_message(
            to=to,
            from_=from_number,
            body=body,
            status=message.status,
            direction="outbound",
            appointment_id=appointment_id,
            twilio_sid=message.sid
        )
        
        return {
            "success": True,
            "sid": message.sid,
            "status": message.status,
            "log_id": log_id
        }
        
    except Exception as e:
        # Log error
        log_id = await log_twilio_message(
            to=to,
            from_=from_number,
            body=body,
            status="failed",
            direction="outbound",
            appointment_id=appointment_id,
            error_message=str(e)
        )
        
        print(f"❌ Failed to send SMS to {to}: {str(e)}")
        
        return {
            "success": False,
            "error": str(e),
            "log_id": log_id
        }


async def send_reminder_sms(appointment: Dict[str, Any]):
    """
    Send 3-hour reminder SMS to patient
    """
    users_collection = get_users_collection()
    
    # Get patient info
    try:
        patient = await users_collection.find_one({"_id": ObjectId(appointment["patientId"])})
    except Exception:
        print(f"❌ Invalid patient ID: {appointment['patientId']}")
        return
    
    if not patient:
        print(f"❌ Patient not found: {appointment['patientId']}")
        return
    
    # Get doctor info
    try:
        doctor = await users_collection.find_one({"_id": ObjectId(appointment["doctorId"])})
    except Exception:
        print(f"❌ Invalid doctor ID: {appointment['doctorId']}")
        return
    
    if not doctor:
        print(f"❌ Doctor not found: {appointment['doctorId']}")
        return
    
    # Format appointment time
    start_time = appointment["start"].strftime("%I:%M %p")
    date_str = appointment["start"].strftime("%d %b %Y")
    
    # Simple message format to avoid carrier blocking
    appointment_id = str(appointment["_id"])
    body = (
        f"Health Clinic: {date_str} at {start_time}\n"
        f"{doctor['name']}\n"
        f"Please confirm on our website"
    )
    
    # Send SMS
    result = await send_sms(
        to=patient["phone"],
        body=body,
        from_number=settings.TWILIO_FROM_PATIENT,
        appointment_id=appointment_id
    )
    
    if result["success"]:
        # Add log ID to appointment
        from app.core.db import get_appointments_collection
        appointments_collection = get_appointments_collection()
        
        await appointments_collection.update_one(
            {"_id": appointment["_id"]},
            {"$push": {"twilioLogs": result["log_id"]}}
        )


async def send_no_show_notification(appointment: Dict[str, Any]):
    """
    Send no-show notification to both patient and doctor
    Smart filtering: Only sends to real phone numbers (skips +1555* test numbers)
    """
    users_collection = get_users_collection()
    
    # Get patient and doctor
    try:
        patient = await users_collection.find_one({"_id": ObjectId(appointment["patientId"])})
        doctor = await users_collection.find_one({"_id": ObjectId(appointment["doctorId"])})
    except Exception as e:
        print(f"❌ Error fetching user data: {str(e)}")
        return
    
    if not patient or not doctor:
        print(f"❌ Patient or doctor not found for no-show notification")
        return
    
    start_time = appointment["start"].strftime("%B %d, %Y at %I:%M %p UTC")
    
    # Message to patient
    patient_body = (
        f"Your appointment with {doctor['name']} on {start_time} "
        f"has been marked as a no-show. Please contact the clinic if this is an error."
    )
    
    # Message to doctor
    doctor_body = (
        f"Patient {patient['name']} did not show up for the appointment on {start_time}. "
        f"Appointment has been marked as no-show."
    )
    
    # Send to both (will auto-skip test numbers)
    await send_sms(
        to=patient["phone"],
        body=patient_body,
        from_number=settings.TWILIO_FROM_PATIENT,
        appointment_id=str(appointment["_id"])
    )
    
    await send_sms(
        to=doctor["phone"],
        body=doctor_body,
        from_number=settings.TWILIO_FROM_DOCTOR,
        appointment_id=str(appointment["_id"])
    )


async def send_confirmation_notification(appointment: Dict[str, Any]):
    """
    Send confirmation notification to doctor
    Smart filtering: Only sends to real phone numbers (skips +1555* test numbers)
    """
    users_collection = get_users_collection()
    
    try:
        patient = await users_collection.find_one({"_id": ObjectId(appointment["patientId"])})
        doctor = await users_collection.find_one({"_id": ObjectId(appointment["doctorId"])})
    except Exception as e:
        print(f"❌ Error fetching user data: {str(e)}")
        return
    
    if not patient or not doctor:
        return
    
    start_time = appointment["start"].strftime("%B %d, %Y at %I:%M %p UTC")
    
    body = (
        f"Patient {patient['name']} has confirmed their appointment on {start_time}."
    )
    
    await send_sms(
        to=doctor["phone"],
        body=body,
        from_number=settings.TWILIO_FROM_DOCTOR,
        appointment_id=str(appointment["_id"])
    )


async def send_cancellation_notification(appointment: Dict[str, Any]):
    """
    Send cancellation notification to doctor
    Smart filtering: Only sends to real phone numbers (skips +1555* test numbers)
    """
    users_collection = get_users_collection()
    
    try:
        patient = await users_collection.find_one({"_id": ObjectId(appointment["patientId"])})
        doctor = await users_collection.find_one({"_id": ObjectId(appointment["doctorId"])})
    except Exception as e:
        print(f"❌ Error fetching user data: {str(e)}")
        return
    
    if not patient or not doctor:
        return
    
    start_time = appointment["start"].strftime("%B %d, %Y at %I:%M %p UTC")
    
    body = (
        f"Patient {patient['name']} has cancelled their appointment on {start_time}."
    )
    
    await send_sms(
        to=doctor["phone"],
        body=body,
        from_number=settings.TWILIO_FROM_DOCTOR,
        appointment_id=str(appointment["_id"])
    )
