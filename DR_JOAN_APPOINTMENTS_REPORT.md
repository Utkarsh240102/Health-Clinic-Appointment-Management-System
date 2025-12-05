# 📋 Appointment Check Report - Dr. Joan Prince

**Generated:** December 5, 2025 at 6:44 PM UTC

---

## 👨‍⚕️ Doctor Information

- **Name:** Dr. Joan Prince
- **Email:** doctor2@clinic.com
- **Password:** Doctor2Pass *(from .env file)*
- **Specialization:** Dermatology
- **Total Upcoming Appointments:** 9

---

## 📅 Upcoming Appointments & SMS Schedule

### Appointment #1
- **Date & Time:** December 8, 2025 at 2:00 PM UTC
- **Status:** Scheduled
- **Reason:** Preventive care
- **3-Hour SMS Reminder:** December 8, 2025 at 11:00 AM UTC
- **Reminder will be sent in:** 64.3 hours (approximately 2 days, 16 hours)

### Appointment #2
- **Date & Time:** December 8, 2025 at 2:30 PM UTC
- **Status:** Scheduled
- **Reason:** testing
- **3-Hour SMS Reminder:** December 8, 2025 at 11:30 AM UTC
- **Reminder will be sent in:** 64.8 hours (approximately 2 days, 16.8 hours)

### Appointment #3
- **Date & Time:** December 10, 2025 at 3:00 PM UTC
- **Status:** Scheduled
- **Reason:** Specialist consultation
- **3-Hour SMS Reminder:** December 10, 2025 at 12:00 PM UTC
- **Reminder will be sent in:** 113.3 hours (approximately 4 days, 17 hours)

### Appointment #4
- **Date & Time:** December 10, 2025 at 4:00 PM UTC
- **Status:** Scheduled
- **Reason:** Symptoms evaluation
- **3-Hour SMS Reminder:** December 10, 2025 at 1:00 PM UTC
- **Reminder will be sent in:** 114.3 hours (approximately 4 days, 18 hours)

### Appointment #5
- **Date & Time:** December 15, 2025 at 10:30 AM UTC
- **Status:** Scheduled
- **Reason:** Vaccination
- **3-Hour SMS Reminder:** December 15, 2025 at 7:30 AM UTC
- **Reminder will be sent in:** 228.8 hours (approximately 9 days, 13 hours)

---

## ⏰ Twilio SMS Timing Explained

### How It Works:
1. **Scheduler Runs:** Every minute, APScheduler checks for appointments
2. **3-Hour Reminder:** SMS is sent 3 hours before appointment start time
3. **Condition:** Only sent for appointments with status "scheduled" or "confirmed"
4. **One-Time:** Each reminder is sent only once (tracked by `reminder3hSent` flag)

### Example Timeline for Appointment #1:
```
Current Time:     Dec 5, 2025 at 6:44 PM UTC
Reminder Time:    Dec 8, 2025 at 11:00 AM UTC  ← SMS will be sent here
Appointment Time: Dec 8, 2025 at 2:00 PM UTC   ← Patient arrives here
```

### SMS Content:
```
Appointment Reminder: You have an appointment with 
Dr. Joan Prince on December 8, 2025 at 2:00 PM. 
Reason: Preventive care. Please confirm your appointment.
```

### No-Show Detection:
- If patient doesn't show up 15 minutes after appointment start
- Status automatically changed to "no_show"
- Another SMS notification is sent

---

## 🔍 How to Verify SMS Sending

### Method 1: Check Appointment After Reminder Time
```bash
# Run this after Dec 8, 2025 at 11:00 AM UTC
cd backend
.\venv\Scripts\Activate.ps1
python check_appointments.py
# Look for "SMS Status: ✅ Already sent"
```

### Method 2: Check Twilio Logs in Database
```python
# In MongoDB or Python shell
appointment = db.appointments.find_one({'start': datetime(2025, 12, 8, 14, 0, 0)})
print(appointment['twilioLogs'])
# Should show: [{'type': 'reminder', 'sentAt': '...', 'status': 'sent'}]
```

### Method 3: Check Twilio Dashboard
1. Go to https://console.twilio.com/
2. Click "Monitor" → "Logs" → "Messaging"
3. Filter by date: December 8, 2025
4. Look for SMS sent at 11:00 AM UTC

---

## 🧪 Testing SMS Immediately

If you want to test SMS without waiting, you can temporarily modify the reminder time:

### Option 1: Change Appointment Time
```python
# Set appointment to 4 minutes from now
from datetime import datetime, timedelta
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def update():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    # Set appointment to 4 minutes from now (3-hour reminder = 1 minute from now)
    new_time = datetime.utcnow() + timedelta(minutes=4)
    
    await db.appointments.update_one(
        {'start': datetime(2025, 12, 8, 14, 0, 0)},
        {'$set': {'start': new_time, 'reminder3hSent': False}}
    )
    print(f"Updated appointment to: {new_time}")
    client.close()

asyncio.run(update())
```

### Option 2: Use Testing Script
```bash
cd backend
python restore_twilio_settings.py  # Changes reminder to 1 minute
# Wait 1 minute after booking appointment
# SMS will be sent
python restore_twilio_settings.py  # Restore to 3 hours
```

---

## 📊 Current System Status

- **Current UTC Time:** December 5, 2025 at 6:44 PM
- **Scheduler Status:** Running (checks every minute)
- **Next Reminder:** December 8, 2025 at 11:00 AM UTC (in ~64 hours)
- **Reminder Configuration:** 3 hours before appointment
- **No-Show Detection:** 15 minutes after appointment start

---

## 🎯 Summary

**Dr. Joan Prince** has **9 upcoming appointments**, with the first one scheduled for:
- **December 8, 2025 at 2:00 PM UTC**

The Twilio SMS reminder will be automatically sent:
- **December 8, 2025 at 11:00 AM UTC** (3 hours before)
- **That's in approximately 64 hours from now**

The system is working correctly, and reminders will be sent automatically by APScheduler! ✅
