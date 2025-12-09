"""
Check when SMS reminder will be sent for 9 AM appointment
"""
from datetime import datetime, timedelta
import pytz

# Current UTC time
now = datetime.now(pytz.UTC)

# Appointment at 9 AM UTC today/tomorrow
appt_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
if appt_time <= now:
    appt_time += timedelta(days=1)

# 3-hour reminder
reminder_time = appt_time - timedelta(hours=3)

print("=" * 60)
print("📅 APPOINTMENT REMINDER TIMING")
print("=" * 60)
print(f"\n⏰ Current UTC Time:    {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"📆 Appointment Time:    {appt_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"📱 SMS Reminder Time:   {reminder_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"\n⏳ Time until reminder: {(reminder_time - now).total_seconds() / 60:.1f} minutes")

# Convert to IST for user reference
ist = pytz.timezone('Asia/Kolkata')
reminder_ist = reminder_time.astimezone(ist)
appt_ist = appt_time.astimezone(ist)

print("\n" + "=" * 60)
print("🇮🇳 INDIAN TIME (IST) - Your Local Time")
print("=" * 60)
print(f"📱 SMS Reminder:        {reminder_ist.strftime('%Y-%m-%d %I:%M %p IST')}")
print(f"📆 Appointment:         {appt_ist.strftime('%Y-%m-%d %I:%M %p IST')}")
print("=" * 60)
