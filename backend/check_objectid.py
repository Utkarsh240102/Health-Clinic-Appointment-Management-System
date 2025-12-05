"""
Check ObjectId types in appointments
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings

async def check_objectid_types():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    print("=" * 60)
    print("CHECKING OBJECTID TYPES")
    print("=" * 60)
    
    # Get one recent appointment
    apt = await db.appointments.find_one({'reason': {'$regex': 'testing', '$options': 'i'}})
    
    if apt:
        print(f"\nAppointment ID: {apt['_id']}")
        print(f"Reason: {apt.get('reason')}")
        print(f"\nDoctorId value: {apt.get('doctorId')}")
        print(f"DoctorId type: {type(apt.get('doctorId'))}")
        print(f"\nPatientId value: {apt.get('patientId')}")
        print(f"PatientId type: {type(apt.get('patientId'))}")
        
        # Try to find using the exact value
        print("\n" + "=" * 60)
        print("TRYING TO FIND DOCTOR")
        print("=" * 60)
        
        doctor_id = apt.get('doctorId')
        print(f"\nSearching for doctor with _id: {doctor_id} (type: {type(doctor_id)})")
        
        # Try as-is
        doctor1 = await db.users.find_one({'_id': doctor_id})
        print(f"Direct search: {doctor1 is not None}")
        
        # Try converting to ObjectId if it's a string
        if isinstance(doctor_id, str):
            try:
                doctor_id_obj = ObjectId(doctor_id)
                doctor2 = await db.users.find_one({'_id': doctor_id_obj})
                print(f"Search with ObjectId conversion: {doctor2 is not None}")
                if doctor2:
                    print(f"Doctor name: {doctor2.get('name')}")
            except Exception as e:
                print(f"Error converting to ObjectId: {e}")
        
        # Check user collection
        print("\n" + "=" * 60)
        print("CHECKING USER COLLECTION")
        print("=" * 60)
        user = await db.users.find_one({'email': 'doctor2@clinic.com'})
        if user:
            print(f"Doctor2 _id value: {user['_id']}")
            print(f"Doctor2 _id type: {type(user['_id'])}")
            print(f"Doctor2 name: {user.get('name')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_objectid_types())
