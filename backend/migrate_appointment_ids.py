"""
Migration script: Convert doctorId and patientId from strings to ObjectIds
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings

async def migrate_appointments():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    print("=" * 60)
    print("MIGRATING APPOINTMENTS: STRING IDS -> OBJECTIDS")
    print("=" * 60)
    
    # Get all appointments
    appointments = await db.appointments.find({}).to_list(None)
    print(f"\nTotal appointments: {len(appointments)}")
    
    migrated = 0
    skipped = 0
    errors = 0
    
    for apt in appointments:
        try:
            doctor_id = apt.get('doctorId')
            patient_id = apt.get('patientId')
            
            # Check if already ObjectIds
            if isinstance(doctor_id, ObjectId) and isinstance(patient_id, ObjectId):
                skipped += 1
                continue
            
            # Convert strings to ObjectIds
            updates = {}
            if isinstance(doctor_id, str):
                updates['doctorId'] = ObjectId(doctor_id)
            if isinstance(patient_id, str):
                updates['patientId'] = ObjectId(patient_id)
            
            if updates:
                await db.appointments.update_one(
                    {'_id': apt['_id']},
                    {'$set': updates}
                )
                migrated += 1
                print(f"✓ Migrated appointment {apt['_id']}")
        
        except Exception as e:
            errors += 1
            print(f"✗ Error migrating {apt['_id']}: {e}")
    
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE")
    print("=" * 60)
    print(f"Migrated: {migrated}")
    print(f"Skipped (already ObjectIds): {skipped}")
    print(f"Errors: {errors}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate_appointments())
