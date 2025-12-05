"""
Check APScheduler job queue
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import pytz

async def check():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["clinic_db"]
    
    # Current time
    ist = pytz.timezone('Asia/Kolkata')
    now_utc = datetime.now(pytz.UTC)
    now_ist = now_utc.astimezone(ist)
    
    print(f"⏰ Current Time: {now_ist.strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("="*80)
    
    # Check APScheduler jobs
    jobs_collection = db["apscheduler_jobs"]
    jobs = await jobs_collection.find().to_list(length=100)
    
    print(f"\n📋 Total jobs in queue: {len(jobs)}")
    
    for job in jobs:
        job_id = job.get('_id')
        next_run = job.get('next_run_time')
        
        if next_run and 'reminder_' in str(job_id):
            next_run_dt = datetime.fromtimestamp(next_run, tz=ist)
            print(f"\n🔔 Job: {job_id}")
            print(f"   Next Run: {next_run_dt.strftime('%Y-%m-%d %H:%M:%S IST')}")
    
    # Check recent appointments
    appointments = db["appointments"]
    recent = await appointments.find().sort("createdAt", -1).limit(5).to_list(length=5)
    
    print(f"\n\n📅 Recent 5 Appointments:")
    print("="*80)
    for apt in recent:
        print(f"\n🏥 ID: {apt['_id']}")
        print(f"   Start: {apt.get('start')}")
        print(f"   Status: {apt.get('status')}")
        print(f"   Reminder Sent: {apt.get('reminder3hSent', False)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check())
