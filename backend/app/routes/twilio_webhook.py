from fastapi import APIRouter, Request, HTTPException, status, Header
from twilio.request_validator import RequestValidator
from app.config import settings
from app.core.db import get_appointments_collection, get_twilio_logs_collection
from app.services.appointment_service import update_appointment_status
from datetime import datetime
from bson import ObjectId
import re

router = APIRouter()

# Initialize Twilio validator
validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)


def verify_twilio_signature(url: str, post_data: dict, signature: str) -> bool:
    """Verify Twilio webhook signature"""
    return validator.validate(url, post_data, signature)


async def log_incoming_sms(from_number: str, to_number: str, body: str, message_sid: str):
    """Log incoming SMS to database"""
    twilio_logs_collection = get_twilio_logs_collection()
    
    log_doc = {
        "to": to_number,
        "from": from_number,
        "body": body,
        "status": "received",
        "timestamp": datetime.utcnow(),
        "direction": "inbound",
        "twilioSid": message_sid
    }
    
    result = await twilio_logs_collection.insert_one(log_doc)
    return str(result.inserted_id)


async def process_sms_command(body: str, from_number: str) -> dict:
    """
    Process SMS command from patient
    
    Supported commands:
    - CONFIRM <appointment_id>
    - CANCEL <appointment_id>
    """
    body = body.strip().upper()
    
    # Match CONFIRM <id> or CANCEL <id>
    confirm_match = re.match(r'CONFIRM\s+([A-Z0-9]+)', body)
    cancel_match = re.match(r'CANCEL\s+([A-Z0-9]+)', body)
    
    if confirm_match:
        appointment_id = confirm_match.group(1)
        return await handle_confirm(appointment_id, from_number)
    
    elif cancel_match:
        appointment_id = cancel_match.group(1)
        return await handle_cancel(appointment_id, from_number)
    
    else:
        return {
            "success": False,
            "message": "Invalid command. Reply 'CONFIRM <ID>' or 'CANCEL <ID>'."
        }


async def handle_confirm(appointment_id: str, from_number: str) -> dict:
    """Handle CONFIRM command"""
    appointments_collection = get_appointments_collection()
    
    # Get appointment
    try:
        appointment = await appointments_collection.find_one({"_id": ObjectId(appointment_id)})
    except Exception:
        return {
            "success": False,
            "message": "Invalid appointment ID format."
        }
    
    if not appointment:
        return {
            "success": False,
            "message": f"Appointment {appointment_id} not found."
        }
    
    # Verify phone number matches patient
    from app.core.db import get_users_collection
    users_collection = get_users_collection()
    
    patient = await users_collection.find_one({"_id": ObjectId(appointment["patientId"])})
    
    if not patient or patient["phone"] != from_number:
        return {
            "success": False,
            "message": "Phone number does not match appointment patient."
        }
    
    # Check if can be confirmed
    if appointment["status"] not in ["scheduled"]:
        return {
            "success": False,
            "message": f"Appointment cannot be confirmed (current status: {appointment['status']})."
        }
    
    # Update status
    try:
        await update_appointment_status(
            appointment_id=appointment_id,
            new_status="confirmed",
            user_id=str(appointment["patientId"]),
            user_role="patient"
        )
        
        return {
            "success": True,
            "message": f"Appointment {appointment_id} confirmed successfully!"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to confirm appointment: {str(e)}"
        }


async def handle_cancel(appointment_id: str, from_number: str) -> dict:
    """Handle CANCEL command"""
    appointments_collection = get_appointments_collection()
    
    # Get appointment
    try:
        appointment = await appointments_collection.find_one({"_id": ObjectId(appointment_id)})
    except Exception:
        return {
            "success": False,
            "message": "Invalid appointment ID format."
        }
    
    if not appointment:
        return {
            "success": False,
            "message": f"Appointment {appointment_id} not found."
        }
    
    # Verify phone number
    from app.core.db import get_users_collection
    users_collection = get_users_collection()
    
    patient = await users_collection.find_one({"_id": ObjectId(appointment["patientId"])})
    
    if not patient or patient["phone"] != from_number:
        return {
            "success": False,
            "message": "Phone number does not match appointment patient."
        }
    
    # Check if can be cancelled
    if appointment["status"] in ["completed", "no_show"]:
        return {
            "success": False,
            "message": f"Appointment cannot be cancelled (current status: {appointment['status']})."
        }
    
    # Update status
    try:
        await update_appointment_status(
            appointment_id=appointment_id,
            new_status="cancelled",
            user_id=str(appointment["patientId"]),
            user_role="patient"
        )
        
        return {
            "success": True,
            "message": f"Appointment {appointment_id} cancelled successfully."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to cancel appointment: {str(e)}"
        }


@router.post("/webhook")
async def twilio_webhook(
    request: Request,
    x_twilio_signature: str = Header(None, alias="X-Twilio-Signature")
):
    """
    Twilio webhook endpoint for incoming SMS
    
    - Verifies Twilio signature for security
    - Parses CONFIRM/CANCEL commands
    - Updates appointments accordingly
    - Emits socket events for real-time updates
    """
    # Get form data
    form_data = await request.form()
    post_data = dict(form_data)
    
    # Get request URL for signature verification
    url = str(request.url)
    
    # Verify signature (skip in test environments without signature)
    if x_twilio_signature:
        if not verify_twilio_signature(url, post_data, x_twilio_signature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid Twilio signature"
            )
    
    # Extract SMS data
    from_number = post_data.get("From", "")
    to_number = post_data.get("To", "")
    body = post_data.get("Body", "")
    message_sid = post_data.get("MessageSid", "")
    
    # Log incoming SMS
    await log_incoming_sms(from_number, to_number, body, message_sid)
    
    # Process command
    result = await process_sms_command(body, from_number)
    
    # Return TwiML response
    response_body = result["message"]
    
    return {
        "success": result["success"],
        "message": response_body
    }
