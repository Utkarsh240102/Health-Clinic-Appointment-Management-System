"""
Check specific appointment reminder details
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings

async def check_appointment_reminder():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    print("=" * 60)
    print("CHECKING 5:51 AM APPOINTMENT")
    print("=" * 60)
    
    apt = await db.appointments.find_one({'_id': ObjectId('69334c6fd93bd39de0f4da49')})
    
    if apt:
        start_time = apt['start']
        reminder_time = start_time - timedelta(hours=3)
        now = datetime.utcnow()
        
        print(f"\n📅 Appointment ID: {apt['_id']}")
        print(f"Start Time: {start_time}")
        print(f"Status: {apt['status']}")
        print(f"Reminder 3h Sent: {apt.get('reminder3hSent', False)}")
        print(f"Created At: {apt.get('createdAt', 'N/A')}")
        
        print(f"\n⏰ Timing:")
        print(f"Current Time (UTC): {now}")
        print(f"Reminder Should Fire At: {reminder_time} (3 hours before start)")
        print(f"Appointment Start: {start_time}")
        
        time_diff = (reminder_time - now).total_seconds()
        print(f"\nTime until reminder: {time_diff / 60:.1f} minutes")
        
        if time_diff < 0:
            print(f"⚠️ Reminder time has PASSED by {abs(time_diff / 60):.1f} minutes")
        else:
            print(f"✅ Reminder will fire in {time_diff / 60:.1f} minutes")
        
        # Check patient info
        patient = await db.users.find_one({'_id': apt['patientId']})
        if patient:
            print(f"\n👤 Patient: {patient['name']}")
            print(f"Phone: {patient.get('phone', 'MISSING!')}")
            print(f"Email: {patient['email']}")
        
        # Check if reminder job exists
        print(f"\n🔔 Reminder Job ID: reminder_{apt['_id']}")
        print(f"Check queue with: python check_queue.py")
        
        # Check twilio logs
        print(f"\n📱 Twilio Logs: {len(apt.get('twilioLogs', []))}")
        for log_id in apt.get('twilioLogs', []):
            log = await db.twilio_logs.find_one({'_id': log_id})
            if log:
                print(f"  - Status: {log.get('status')}")
                print(f"    Sent At: {log.get('sentAt')}")
                print(f"    Error: {log.get('errorMessage', 'None')}")
    else:
        print("\n❌ Appointment not found!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_appointment_reminder())
