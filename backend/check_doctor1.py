"""
Check appointments for Doctor 1 (Dr. Victoria Welch)
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings

async def check_doctor_appointments():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    print("=" * 60)
    print("DOCTOR 1 APPOINTMENTS")
    print("=" * 60)
    
    # Get Doctor 1
    doctor = await db.users.find_one({'email': 'doctor1@clinic.com'})
    
    if doctor:
        print(f"\n👨‍⚕️ Doctor: {doctor['name']}")
        print(f"Email: {doctor['email']}")
        print(f"ID: {doctor['_id']}")
        
        # Get all appointments for this doctor
        appointments = await db.appointments.find({
            'doctorId': doctor['_id']
        }).sort('start', -1).limit(20).to_list(20)
        
        print(f"\n📅 Total Appointments: {len(appointments)}")
        print("=" * 60)
        
        for i, apt in enumerate(appointments, 1):
            patient = await db.users.find_one({'_id': apt['patientId']})
            
            print(f"\n#{i} - Appointment ID: {apt['_id']}")
            print(f"   Patient: {patient['name'] if patient else 'Unknown'}")
            print(f"   Start: {apt['start']}")
            print(f"   Status: {apt['status']}")
            print(f"   Reason: {apt.get('reason', 'N/A')}")
            print(f"   Reminder Sent: {apt.get('reminder3hSent', False)}")
            
            # Check if appointment has reminder job
            reminder_job_id = f"reminder_{apt['_id']}"
            print(f"   Reminder Job: {reminder_job_id}")
    else:
        print("\n❌ Doctor 1 not found!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_doctor_appointments())
