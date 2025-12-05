# Twilio SMS Messages

## 1. 3-Hour Reminder to Patient

**When:** Sent 3 hours (TEST MODE: 1 minute) before appointment  
**To:** Patient's phone  
**From:** TWILIO_FROM_PATIENT number  
**Message:**
```
Health Clinic: [DATE] at [TIME]
Dr. [DOCTOR_NAME]
Please confirm on our website
```

**Example:**
```
Health Clinic: 21 Nov 2025 at 02:30 PM
Dr. Sarah Johnson
Please confirm on our website
```

---

## 2. No-Show Notification to Patient

**When:** Sent when appointment start time is 15+ minutes (TEST MODE: 2 minutes) past and status is still scheduled/confirmed  
**To:** Patient's phone  
**From:** TWILIO_FROM_PATIENT number  
**Message:**
```
Your appointment with [DOCTOR_NAME] on [FULL_DATE_TIME] has been marked as a no-show. Please contact the clinic if this is an error.
```

**Example:**
```
Your appointment with Dr. Sarah Johnson on November 21, 2025 at 02:30 PM UTC has been marked as a no-show. Please contact the clinic if this is an error.
```

---

## 3. No-Show Notification to Doctor

**When:** Sent simultaneously with patient no-show notification  
**To:** Doctor's phone  
**From:** TWILIO_FROM_DOCTOR number  
**Message:**
```
Patient [PATIENT_NAME] did not show up for the appointment on [FULL_DATE_TIME]. Appointment has been marked as no-show.
```

**Example:**
```
Patient John Doe did not show up for the appointment on November 21, 2025 at 02:30 PM UTC. Appointment has been marked as no-show.
```

---

## 4. Confirmation Notification to Doctor

**When:** Sent when patient confirms appointment (via Twilio webhook response)  
**To:** Doctor's phone  
**From:** TWILIO_FROM_DOCTOR number  
**Message:**
```
Patient [PATIENT_NAME] has confirmed their appointment on [FULL_DATE_TIME].
```

**Example:**
```
Patient John Doe has confirmed their appointment on November 21, 2025 at 02:30 PM UTC.
```

---

## 5. Cancellation Notification to Doctor

**When:** Sent when patient cancels appointment (via Twilio webhook response)  
**To:** Doctor's phone  
**From:** TWILIO_FROM_DOCTOR number  
**Message:**
```
Patient [PATIENT_NAME] has cancelled their appointment on [FULL_DATE_TIME].
```

**Example:**
```
Patient John Doe has cancelled their appointment on November 21, 2025 at 02:30 PM UTC.
```

---

## Testing Configuration

### Original Settings (Production):
- **Reminder Time:** 3 hours before appointment
- **No-Show Threshold:** 15 minutes after appointment start

### Test Settings (For Quick Testing):
- **Reminder Time:** 1 minute before appointment
- **No-Show Threshold:** 2 minutes after appointment start

### To Test:
1. Create an appointment for 3 minutes from now
2. Wait 1 minute → Patient receives reminder SMS
3. Do NOT confirm or cancel the appointment
4. Wait 2 more minutes after appointment start time → Both patient and doctor receive no-show notifications

### To Restore Original Settings:
Run the restoration command after testing is complete (will be provided in terminal).
