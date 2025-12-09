"""
Check 5:51 AM appointment status
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings

async def check_appointment():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    print("=" * 60)
    print("5:51 AM APPOINTMENT STATUS")
    print("=" * 60)
    
    apt = await db.appointments.find_one({'_id': ObjectId('69334c6fd93bd39de0f4da49')})
    
    if apt:
        print(f"\nAppointment ID: {apt['_id']}")
        print(f"Current Status: {apt['status']}")
        print(f"Start Time: {apt['start']}")
        print(f"Reminder Sent: {apt.get('reminder3hSent', False)}")
        
        patient = await db.users.find_one({'_id': apt['patientId']})
        print(f"\nPatient: {patient['name'] if patient else 'Not found'}")
        print(f"Patient ID: {apt['patientId']}")
        
        # Check if it can be confirmed
        if apt['status'] == 'confirmed':
            print(f"\n⚠️ ALREADY CONFIRMED - Cannot confirm again!")
        elif apt['status'] == 'scheduled':
            print(f"\n✅ Can be confirmed (status is 'scheduled')")
        else:
            print(f"\n❌ Cannot confirm - status is '{apt['status']}'")
    else:
        print("\n❌ Appointment not found!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_appointment())
