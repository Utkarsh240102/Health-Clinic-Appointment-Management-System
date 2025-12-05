"""
Check doctor appointments and Twilio SMS schedule
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

async def check_doctors_and_appointments():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    # Find all doctors
    print("=" * 60)
    print("DOCTORS IN DATABASE")
    print("=" * 60)
    doctors = await db.users.find({'role': 'doctor'}).to_list(None)
    
    for i, doctor in enumerate(doctors, 1):
        name = doctor.get('name', 'Unknown')
        email = doctor.get('email', 'N/A')
        specialization = doctor.get('doctorProfile', {}).get('specialization', 'N/A')
        print(f"{i}. {name}")
        print(f"   Email: {email}")
        print(f"   Specialization: {specialization}")
        print()
    
    # Find doctor with name containing "joan" (case insensitive)
    joan_doctors = [d for d in doctors if 'joan' in d.get('name', '').lower() or 'john' in d.get('name', '').lower()]
    
    if not joan_doctors:
        print("\n❌ No doctor found with name containing 'Joan' or 'John'")
        print("\nSearching for appointments of all doctors...")
        target_doctors = doctors[:3]  # Check first 3 doctors
    else:
        print(f"\n✅ Found {len(joan_doctors)} doctor(s) matching 'Joan/John':")
        for d in joan_doctors:
            print(f"   - {d['name']} ({d['email']})")
        target_doctors = joan_doctors
    
    # Check appointments for these doctors
    print("\n" + "=" * 60)
    print("APPOINTMENTS & TWILIO SMS SCHEDULE")
    print("=" * 60)
    
    now = datetime.utcnow()
    
    for doctor in target_doctors:
        doctor_id = str(doctor['_id'])
        doctor_name = doctor.get('name', 'Unknown')
        
        # Get future appointments (scheduled or confirmed)
        appointments = await db.appointments.find({
            'doctorId': doctor_id,
            'start': {'$gte': now},
            'status': {'$in': ['scheduled', 'confirmed']}
        }).sort('start', 1).to_list(None)
        
        print(f"\n📅 Doctor: {doctor_name}")
        print(f"   Total upcoming appointments: {len(appointments)}")
        
        if not appointments:
            print("   ℹ️  No upcoming appointments")
            continue
        
        for i, apt in enumerate(appointments[:5], 1):  # Show first 5
            start = apt['start']
            status = apt['status']
            reason = apt.get('reason', 'N/A')
            reminder_sent = apt.get('reminder3hSent', False)
            
            # Calculate when 3-hour reminder will be sent
            reminder_time = start - timedelta(hours=3)
            time_until_reminder = reminder_time - now
            
            print(f"\n   Appointment #{i}:")
            print(f"   • Start Time: {start.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"   • Status: {status}")
            print(f"   • Reason: {reason}")
            print(f"   • 3-Hour Reminder Time: {reminder_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            if reminder_sent:
                print(f"   • SMS Status: ✅ Already sent")
            elif time_until_reminder.total_seconds() < 0:
                print(f"   • SMS Status: ⚠️  Reminder time passed (should have been sent)")
            elif time_until_reminder.total_seconds() < 3600:  # Less than 1 hour
                minutes = int(time_until_reminder.total_seconds() / 60)
                print(f"   • SMS Status: 🔜 Will be sent in {minutes} minutes")
            else:
                hours = time_until_reminder.total_seconds() / 3600
                print(f"   • SMS Status: ⏰ Will be sent in {hours:.1f} hours")
            
            # Check Twilio logs
            twilio_logs = apt.get('twilioLogs', [])
            if twilio_logs:
                print(f"   • Twilio Logs: {len(twilio_logs)} message(s)")
                for log in twilio_logs:
                    log_type = log.get('type', 'unknown')
                    sent_at = log.get('sentAt', 'N/A')
                    print(f"     - {log_type}: {sent_at}")
    
    print("\n" + "=" * 60)
    print("SCHEDULER INFO")
    print("=" * 60)
    print(f"Current UTC Time: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Reminder Schedule: 3 hours before appointment start")
    print(f"No-Show Detection: 15 minutes after appointment start")
    print(f"Scheduler runs: Every minute (checks for reminders to send)")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_doctors_and_appointments())
