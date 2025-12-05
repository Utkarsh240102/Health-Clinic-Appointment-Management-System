"""
Check appointments in MongoDB
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings

async def check_appointments():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    # Get all appointments from Dec 8 onwards
    print("=" * 60)
    print("CHECKING APPOINTMENTS IN MONGODB")
    print("=" * 60)
    
    appointments = await db.appointments.find({
        'start': {'$gte': datetime(2025, 12, 8)}
    }).sort('start', 1).to_list(None)
    
    print(f"\nTotal appointments on/after Dec 8: {len(appointments)}")
    
    # Get doctor and patient info
    for i, apt in enumerate(appointments[:15], 1):
        doctor = await db.users.find_one({'_id': apt['doctorId']})
        patient = await db.users.find_one({'_id': apt['patientId']})
        
        print(f"\n{'='*60}")
        print(f"Appointment #{i}")
        print(f"{'='*60}")
        print(f"ID: {apt['_id']}")
        print(f"Doctor: {doctor.get('name', 'Unknown') if doctor else 'Not found'}")
        print(f"Patient: {patient.get('name', 'Unknown') if patient else 'Not found'}")
        print(f"Start Time: {apt['start']}")
        print(f"Status: {apt['status']}")
        print(f"Reason: {apt.get('reason', 'N/A')}")
        print(f"Reminder Sent: {apt.get('reminder3hSent', False)}")
        print(f"Created At: {apt.get('createdAt', 'N/A')}")
    
    # Check for "Testing" reason specifically
    print(f"\n{'='*60}")
    print("APPOINTMENTS WITH 'TESTING' REASON")
    print(f"{'='*60}")
    
    testing_apts = await db.appointments.find({
        'reason': {'$regex': 'testing', '$options': 'i'}
    }).to_list(None)
    
    print(f"\nFound {len(testing_apts)} appointment(s) with 'testing' reason:")
    for apt in testing_apts:
        doctor = await db.users.find_one({'_id': apt['doctorId']})
        patient = await db.users.find_one({'_id': apt['patientId']})
        print(f"\nID: {apt['_id']}")
        print(f"Doctor: {doctor.get('name', 'Unknown') if doctor else 'Not found'}")
        print(f"Patient: {patient.get('name', 'Unknown') if patient else 'Not found'}")
        print(f"Start: {apt['start']}")
        print(f"Status: {apt['status']}")
        print(f"Reason: {apt.get('reason', 'N/A')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_appointments())
