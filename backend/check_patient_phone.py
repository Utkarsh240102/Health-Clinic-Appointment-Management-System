"""
Check patient phone and appointment details
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings

async def check_patient_phone():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    print("=" * 60)
    print("CHECKING APPOINTMENT AND PATIENT PHONE")
    print("=" * 60)
    
    apt = await db.appointments.find_one({'_id': ObjectId('693343001bfdc05743f58bf9')})
    
    if apt:
        print(f"\n📅 Appointment ID: {apt['_id']}")
        print(f"Patient ID: {apt['patientId']}")
        print(f"Doctor ID: {apt['doctorId']}")
        print(f"Status: {apt['status']}")
        print(f"Start: {apt['start']}")
        print(f"Reminder Sent: {apt.get('reminder3hSent', False)}")
        
        # Get patient
        patient = await db.users.find_one({'_id': apt['patientId']})
        if patient:
            print(f"\n👤 Patient: {patient.get('name')}")
            print(f"Email: {patient.get('email')}")
            print(f"Phone: {patient.get('phone', '⚠️ MISSING!')}")
            print(f"Role: {patient.get('role')}")
        else:
            print("\n❌ Patient not found!")
        
        # Get doctor
        doctor = await db.users.find_one({'_id': apt['doctorId']})
        if doctor:
            print(f"\n👨‍⚕️ Doctor: {doctor.get('name')}")
            print(f"Email: {doctor.get('email')}")
        else:
            print("\n❌ Doctor not found!")
    else:
        print("\n❌ Appointment not found!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_patient_phone())
