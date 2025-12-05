"""
Check users and appointment relationships
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings

async def check_users():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    print("=" * 60)
    print("USERS IN DATABASE")
    print("=" * 60)
    
    # Get all users
    users = await db.users.find({}).to_list(None)
    print(f"\nTotal users: {len(users)}")
    
    for user in users:
        print(f"\nID: {user['_id']}")
        print(f"Name: {user.get('name', 'N/A')}")
        print(f"Email: {user.get('email', 'N/A')}")
        print(f"Role: {user.get('role', 'N/A')}")
    
    # Check recent appointments
    print("\n" + "=" * 60)
    print("RECENT APPOINTMENTS (Last 10)")
    print("=" * 60)
    
    appointments = await db.appointments.find({}).sort('createdAt', -1).limit(10).to_list(None)
    
    for i, apt in enumerate(appointments, 1):
        print(f"\n--- Appointment #{i} ---")
        print(f"ID: {apt['_id']}")
        print(f"DoctorId: {apt.get('doctorId', 'N/A')}")
        print(f"PatientId: {apt.get('patientId', 'N/A')}")
        print(f"Start: {apt['start']}")
        print(f"Status: {apt['status']}")
        print(f"Reason: {apt.get('reason', 'N/A')}")
        print(f"Created: {apt.get('createdAt', 'N/A')}")
        
        # Try to find matching users
        doctor = await db.users.find_one({'_id': apt.get('doctorId')})
        patient = await db.users.find_one({'_id': apt.get('patientId')})
        print(f"Doctor Found: {doctor is not None} ({doctor.get('name') if doctor else 'N/A'})")
        print(f"Patient Found: {patient is not None} ({patient.get('name') if patient else 'N/A'})")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_users())
