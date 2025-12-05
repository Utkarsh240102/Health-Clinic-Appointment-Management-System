"""
Scheduler service for managing appointment reminders and no-show detection
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.core.db import get_appointments_collection
from bson import ObjectId
from pymongo import ReturnDocument


async def send_3h_reminder(appointment_id: str):
    """
    Send 3-hour reminder SMS to patient
    Called by APScheduler job
    """
    from app.services.twilio_service import send_reminder_sms
    
    appointments_collection = get_appointments_collection()
    
    # Get appointment
    try:
        appointment = await appointments_collection.find_one({"_id": ObjectId(appointment_id)})
    except Exception:
        print(f"❌ Invalid appointment ID in reminder job: {appointment_id}")
        return
    
    if not appointment:
        print(f"❌ Appointment not found for reminder: {appointment_id}")
        return
    
    # Check if appointment is still active
    if appointment["status"] not in ["scheduled", "confirmed"]:
        print(f"ℹ️ Appointment {appointment_id} is {appointment['status']}, skipping reminder")
        return
    
    # Send reminder SMS
    try:
        await send_reminder_sms(appointment)
        
        # Mark reminder as sent
        await appointments_collection.update_one(
            {"_id": ObjectId(appointment_id)},
            {"$set": {"reminder3hSent": True}}
        )
        
        print(f"✅ Sent 3h reminder for appointment {appointment_id}")
        
    except Exception as e:
        print(f"❌ Failed to send reminder for {appointment_id}: {str(e)}")


async def schedule_reminder_job(appointment_id: str, reminder_time: datetime, scheduler=None) -> Optional[Dict[str, Any]]:
    """
    Schedule a reminder job for an appointment using APScheduler
    """
    if scheduler is None:
        from app.main import scheduler as default_scheduler
        scheduler = default_scheduler
    
    try:
        job = scheduler.add_job(
            send_3h_reminder,
            'date',
            run_date=reminder_time,
            args=[appointment_id],
            id=f"reminder_{appointment_id}",
            replace_existing=True
        )
        
        return {
            "job_id": job.id,
            "scheduled_at": reminder_time
        }
    except Exception as e:
        print(f"❌ Failed to schedule reminder job for {appointment_id}: {str(e)}")
        return None


async def auto_cancel_unconfirmed():
    """
    Cron job to auto-cancel appointments that weren't confirmed
    Cancels appointments where:
    - status is 'scheduled' (not confirmed by patient)
    - appointment time is less than 15 minutes away
    - reminder was sent (3h before) but patient didn't confirm within 2:45h
    """
    from app.services.twilio_service import send_cancellation_notification
    
    appointments_collection = get_appointments_collection()
    now = datetime.utcnow()
    
    # Time window: 15 minutes before appointment
    # If patient hasn't confirmed by now, cancel
    cutoff_time = now + timedelta(minutes=15)
    
    # Find scheduled appointments with reminder sent but not confirmed
    cursor = appointments_collection.find({
        "status": "scheduled",
        "reminder3hSent": True,
        "start": {"$lte": cutoff_time, "$gte": now}
    })
    
    cancelled_count = 0
    async for appointment in cursor:
        try:
            # Cancel the appointment
            await appointments_collection.update_one(
                {"_id": appointment["_id"]},
                {
                    "$set": {
                        "status": "cancelled",
                        "cancelledAt": now,
                        "cancelReason": "Auto-cancelled: Not confirmed within required timeframe"
                    }
                }
            )
            
            # Send cancellation SMS
            try:
                await send_cancellation_notification(appointment)
            except Exception as e:
                print(f"⚠️ Failed to send cancellation SMS for {appointment['_id']}: {str(e)}")
            
            cancelled_count += 1
            print(f"✅ Auto-cancelled unconfirmed appointment {appointment['_id']}")
            
        except Exception as e:
            print(f"❌ Failed to cancel appointment {appointment['_id']}: {str(e)}")
    
    if cancelled_count > 0:
        print(f"📊 Auto-cancelled {cancelled_count} unconfirmed appointment(s)")
    
    return cancelled_count


async def auto_cancel_no_shows():
    """
    Cron job that runs every minute to mark no-shows
    Finds appointments where:
    - status is scheduled or confirmed
    - start time was more than 15 minutes ago
    - appointment not completed
    """
    from app.services.twilio_service import send_no_show_notification
    
    appointments_collection = get_appointments_collection()
    now = datetime.utcnow()
    cutoff_time = now - timedelta(minutes=15)
    
    # Find appointments to mark as no-show
    cursor = appointments_collection.find({
        "status": {"$in": ["scheduled", "confirmed"]},
        "start": {"$lte": cutoff_time}
    })
    
    no_show_count = 0
    async for appointment in cursor:
        try:
            # Update to no_show status
            updated = await appointments_collection.find_one_and_update(
                {"_id": appointment["_id"]},
                {"$set": {"status": "no_show"}},
                return_document=ReturnDocument.AFTER
            )
            
            if updated:
                no_show_count += 1
                print(f"🚫 Marked appointment {appointment['_id']} as no-show")
                
                # Send notifications
                await send_no_show_notification(updated)
                
        except Exception as e:
            print(f"❌ Failed to mark no-show for {appointment['_id']}: {str(e)}")
    
    if no_show_count > 0:
        print(f"✅ Marked {no_show_count} appointments as no-show")


def start_auto_cancel_cron(scheduler):
    """Start the auto-cancel cron jobs"""
    try:
        # Job 1: Auto-cancel unconfirmed appointments (runs every minute)
        scheduler.add_job(
            auto_cancel_unconfirmed,
            'cron',
            minute='*',
            id='auto_cancel_unconfirmed',
            replace_existing=True
        )
        print("✅ Started auto-cancel unconfirmed appointments cron job (runs every minute)")
        
        # Job 2: Mark no-shows (runs every minute)
        scheduler.add_job(
            auto_cancel_no_shows,
            'cron',
            minute='*',
            id='auto_cancel_no_shows',
            replace_existing=True
        )
        print("✅ Started auto-cancel no-shows cron job (runs every minute)")
    except Exception as e:
        print(f"❌ Failed to start auto-cancel cron: {str(e)}")
