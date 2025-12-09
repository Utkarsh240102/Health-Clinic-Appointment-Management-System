"""
Check Twilio logs for appointment
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings

async def check_twilio_logs():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    print("=" * 60)
    print("TWILIO SMS LOGS")
    print("=" * 60)
    
    # Check appointment's twilio logs
    apt = await db.appointments.find_one({'_id': ObjectId('693343001bfdc05743f58bf9')})
    
    if apt:
        print(f"\nAppointment: {apt['_id']}")
        print(f"Status: {apt['status']}")
        print(f"Reminder Sent: {apt.get('reminder3hSent', False)}")
        print(f"\nTwilio Logs ({len(apt.get('twilioLogs', []))}):")
        
        for log in apt.get('twilioLogs', []):
            print(f"\n  Type: {log.get('type')}")
            print(f"  Status: {log.get('status')}")
            print(f"  Sent At: {log.get('sentAt')}")
            print(f"  Message SID: {log.get('messageSid', 'N/A')}")
            print(f"  Error: {log.get('error', 'None')}")
    
    # Check twilio_logs collection
    print("\n" + "=" * 60)
    print("TWILIO LOGS COLLECTION (Recent 5)")
    print("=" * 60)
    
    logs = await db.twilio_logs.find({}).sort('sentAt', -1).limit(5).to_list(5)
    
    for log in logs:
        print(f"\nAppointment: {log.get('appointmentId')}")
        print(f"  Type: {log.get('messageType')}")
        print(f"  Status: {log.get('status')}")
        print(f"  Phone: {log.get('phoneNumber')}")
        print(f"  Sent: {log.get('sentAt')}")
        print(f"  Error: {log.get('errorMessage', 'None')}")
    
    client.close()

from bson import ObjectId

if __name__ == "__main__":
    asyncio.run(check_twilio_logs())
