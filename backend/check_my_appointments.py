"""
Check the actual appointment time stored in database for the user
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings

async def check_user_appointments():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    # Find user by phone
    user = await db.users.find_one({"phone": "+917017982662"})
    
    if not user:
        print("❌ User not found with phone +917017982662")
        return
    
    print(f"✅ Found user: {user['name']} (ID: {user['_id']})")
    print("\n" + "=" * 80)
    
    # Find all appointments for this user
    appointments = await db.appointments.find({
        "patientId": user["_id"],
        "status": {"$in": ["scheduled", "confirmed"]}
    }).sort("start", 1).to_list(length=10)
    
    if not appointments:
        print("❌ No active appointments found")
        return
    
    print(f"📅 ACTIVE APPOINTMENTS ({len(appointments)} found):")
    print("=" * 80)
    
    from datetime import timedelta
    import pytz
    ist = pytz.timezone('Asia/Kolkata')
    
    for apt in appointments:
        start_utc = apt["start"]
        start_ist = start_utc.astimezone(ist)
        reminder_time_utc = start_utc - timedelta(hours=3)
        reminder_time_ist = reminder_time_utc.astimezone(ist)
        
        doctor = await db.users.find_one({"_id": apt["doctorId"]})
        
        print(f"\nAppointment ID: {apt['_id']}")
        print(f"Status: {apt['status']}")
        print(f"Doctor: {doctor['name'] if doctor else 'Unknown'}")
        print(f"📆 Appointment Time (UTC): {start_utc.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🇮🇳 Appointment Time (IST): {start_ist.strftime('%Y-%m-%d %I:%M %p')}")
        print(f"📱 Reminder Time (UTC):     {reminder_time_utc.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🇮🇳 Reminder Time (IST):     {reminder_time_ist.strftime('%Y-%m-%d %I:%M %p')}")
        print(f"Reminder sent: {'Yes ✅' if apt.get('reminder3hSent') else 'No ❌'}")
        print("-" * 80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_user_appointments())
