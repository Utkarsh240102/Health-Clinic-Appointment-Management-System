# Twilio SMS Testing Guide

## Current Test Configuration

The system has been modified for **rapid testing**:
- ⚡ **Reminder SMS**: Sent **1 minute** before appointment (was 3 hours)
- ⚡ **No-Show Detection**: Triggers **2 minutes** after appointment start (was 15 minutes)
- ⚡ **30-Minute Boundaries**: **DISABLED** - appointments can be created at any time (e.g., 14:17, 09:03)
- ⚡ **Doctor Schedule Validation**: **DISABLED** - appointments can be created at any time, regardless of doctor's working hours

## Prerequisites

1. **MongoDB** must be running
2. **Backend server** must be running with valid Twilio credentials in `.env`
3. Valid **phone numbers** for test patient and doctor in the database

## Step-by-Step Testing

### Test 1: Reminder SMS

1. **Create an appointment** for **3 minutes from now**
   - Use POST `/api/v1/appointments` endpoint
   - Or create via any API client (Postman, curl, etc.)

2. **Wait 1 minute** after creation
   - The patient will receive a reminder SMS
   - Message format:
     ```
     Health Clinic: [DATE] at [TIME]
     Dr. [DOCTOR_NAME]
     Please confirm on our website
     ```

3. **Check console logs** for confirmation:
   ```
   ✅ Sent 3h reminder for appointment [APPOINTMENT_ID]
   ```

### Test 2: Confirmation Flow (Optional)

1. **Patient replies** to the reminder SMS with "CONFIRM"
   - Twilio webhook will receive the response
   - Doctor receives confirmation notification:
     ```
     Patient [PATIENT_NAME] has confirmed their appointment on [DATE_TIME].
     ```

### Test 3: Cancellation Flow (Optional)

1. **Patient replies** to the reminder SMS with "CANCEL"
   - Twilio webhook will receive the response
   - Doctor receives cancellation notification:
     ```
     Patient [PATIENT_NAME] has cancelled their appointment on [DATE_TIME].
     ```

### Test 4: No-Show Detection

1. **Create an appointment** for **1 minute from now**
2. **Wait 1 minute** for the appointment time to pass
3. **Do NOT confirm or cancel** the appointment
4. **Wait 2 more minutes** (total 3 minutes from creation)
5. **Both patient and doctor receive no-show notifications:**

   **To Patient:**
   ```
   Your appointment with [DOCTOR_NAME] on [DATE_TIME] has been marked as a no-show. Please contact the clinic if this is an error.
   ```

   **To Doctor:**
   ```
   Patient [PATIENT_NAME] did not show up for the appointment on [DATE_TIME]. Appointment has been marked as no-show.
   ```

6. **Check console logs:**
   ```
   🚫 Marked appointment [APPOINTMENT_ID] as no-show
   ✅ Marked 1 appointments as no-show
   ```

## Monitoring

### Watch Backend Logs
```bash
cd backend
uvicorn app.main:app --reload
```

Look for:
- `✅ Sent 3h reminder for appointment [ID]`
- `🚫 Marked appointment [ID] as no-show`
- `✅ Marked X appointments as no-show`

### Check Database
```javascript
// MongoDB queries to verify
db.appointments.find({status: "no_show"})
db.twilio_logs.find().sort({timestamp: -1}).limit(10)
```

### Check Twilio Logs
Check your actual phone for received SMS messages!

## Troubleshooting

### No SMS Received?

1. **Check Twilio credentials** in `.env`:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_FROM_PATIENT`
   - `TWILIO_FROM_DOCTOR`

2. **Verify phone numbers** are in E.164 format: `+1234567890`

3. **Check Twilio console** for delivery status

4. **Check backend logs** for errors:
   ```
   ❌ Failed to send SMS to [PHONE]: [ERROR]
   ```

### Reminder Not Sent?

1. Verify appointment was created more than 1 minute in the future
2. Check APScheduler is running:
   ```
   ✅ APScheduler started
   ```

### No-Show Not Triggered?

1. Verify appointment status is "scheduled" or "confirmed"
2. Check that 2 minutes have passed since appointment start time
3. Verify cron job is running:
   ```
   ✅ Started auto-cancel no-shows cron job (runs every minute)
   ```

## After Testing: Restore Production Settings

**IMPORTANT:** Restore original timing before production use!

```bash
cd backend
python restore_twilio_settings.py
```

Then **restart the backend server**.

## Production Settings

After restoration:
- ⏰ **Reminder SMS**: 3 hours before appointment
- ⏰ **No-Show Detection**: 15 minutes after appointment start
- ⏰ **Time Boundaries**: Appointments must align to 30-minute slots (e.g., 14:00, 14:30, 15:00)
- ⏰ **Doctor Schedule Validation**: Appointments must be within doctor's working hours

---

## Example API Request

Create a test appointment (3 minutes from now):

```bash
POST http://localhost:8000/api/v1/appointments
Authorization: Bearer YOUR_TOKEN

{
  "doctorId": "DOCTOR_OBJECT_ID",
  "patientId": "PATIENT_OBJECT_ID",
  "start": "2025-11-21T14:30:00Z",  # Adjust to 3 minutes from now
  "end": "2025-11-21T14:45:00Z",    # Adjust accordingly
  "reason": "Testing Twilio SMS"
}
```

Calculate times in Python:
```python
from datetime import datetime, timedelta

now = datetime.utcnow()
start = now + timedelta(minutes=3)
end = start + timedelta(minutes=15)

print(f"Start: {start.isoformat()}Z")
print(f"End: {end.isoformat()}Z")
```
