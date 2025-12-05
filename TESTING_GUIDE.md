# 🧪 API Testing Guide - Clinic Management System

## Prerequisites
- Backend running at: `http://localhost:8000`
- MongoDB running
- Access to API docs: `http://localhost:8000/docs`

---

## 📋 Testing Flow (Recommended Order)

### **Step 1: Server Health Check**
```bash
GET http://localhost:8000/health
```
**Expected:** `{"status": "healthy"}`

---

### **Step 2: Get Server Time**
```bash
GET http://localhost:8000/api/v1/time/now
```
**Expected:**
```json
{
  "utc": "2025-11-17T10:30:00.000000",
  "timestamp": 1700220600
}
```

---

## 🔐 Authentication Routes

### **1. Patient Signup** ✅
```bash
POST http://localhost:8000/api/v1/auth/patient/signup
Content-Type: application/json

{
  "fullName": "John Doe",
  "email": "john.doe@example.com",
  "password": "SecurePass123!",
  "phone": "+919876543210",
  "dateOfBirth": "1990-05-15",
  "gender": "male",
  "address": "123 Main St, City"
}
```

**Expected Response:**
```json
{
  "accessToken": "eyJ...",
  "refreshToken": "eyJ...",
  "tokenType": "bearer",
  "user": {
    "id": "...",
    "email": "john.doe@example.com",
    "fullName": "John Doe",
    "role": "patient",
    "phone": "+919876543210",
    ...
  }
}
```

**Save the `accessToken` for subsequent requests!**

---

### **2. Patient Login** ✅
```bash
POST http://localhost:8000/api/v1/auth/patient/login
Content-Type: application/json

{
  "email": "john.doe@example.com",
  "password": "SecurePass123!"
}
```

---

### **3. Doctor Login** ✅
**Note:** Doctors are pre-seeded. Use credentials from seed script.

```bash
POST http://localhost:8000/api/v1/auth/doctor/login
Content-Type: application/json

{
  "email": "doctor1@clinic.com",
  "password": "Doctor1Pass"
}
```

**Save the doctor's `accessToken` separately!**

---

### **4. Refresh Token** ✅
```bash
POST http://localhost:8000/api/v1/auth/refresh
Content-Type: application/json

{
  "refreshToken": "YOUR_REFRESH_TOKEN_HERE"
}
```

---

## 👤 User Profile Routes

**All requests need `Authorization: Bearer YOUR_ACCESS_TOKEN` header**

### **5. Get Current User Profile** ✅
```bash
GET http://localhost:8000/api/v1/users/me
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

### **6. Update User Profile** ✅
```bash
PATCH http://localhost:8000/api/v1/users/me
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "fullName": "John Updated Doe",
  "phone": "+919876543211",
  "address": "456 New St, City"
}
```

---

### **7. Upload Profile Photo** ✅
```bash
POST http://localhost:8000/api/v1/users/me/photo
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: multipart/form-data

# Upload a file with key "file"
```

**In Swagger UI:** Click "Try it out" > Choose file > Execute

---

## 👨‍⚕️ Doctor Routes

### **8. Get Doctor Available Slots** ✅
```bash
GET http://localhost:8000/api/v1/doctors/{DOCTOR_ID}/slots?date=2025-11-18
Authorization: Bearer YOUR_PATIENT_TOKEN
```

**Replace `{DOCTOR_ID}` with actual doctor ID from login response**

**Expected Response:**
```json
[
  {
    "start": "2025-11-18T09:00:00",
    "end": "2025-11-18T09:30:00",
    "available": true
  },
  {
    "start": "2025-11-18T09:30:00",
    "end": "2025-11-18T10:00:00",
    "available": false
  }
]
```

---

## 📅 Appointment Routes

### **9. Create Appointment** ✅
```bash
POST http://localhost:8000/api/v1/appointments
Authorization: Bearer YOUR_PATIENT_TOKEN
Content-Type: application/json

{
  "doctorId": "DOCTOR_ID_HERE",
  "start": "2025-11-18T10:00:00",
  "reason": "Regular checkup"
}
```

**Expected:** `201 Created` with appointment details
**Note:** Save the appointment `id` for next tests

---

### **10. Get All Appointments** ✅
```bash
# As Patient (sees own appointments)
GET http://localhost:8000/api/v1/appointments
Authorization: Bearer YOUR_PATIENT_TOKEN

# As Doctor (sees own appointments)
GET http://localhost:8000/api/v1/appointments
Authorization: Bearer YOUR_DOCTOR_TOKEN
```

**Query Parameters (optional):**
- `?status=scheduled`
- `?startDate=2025-11-01&endDate=2025-11-30`

---

### **11. Get Single Appointment** ✅
```bash
GET http://localhost:8000/api/v1/appointments/{APPOINTMENT_ID}
Authorization: Bearer YOUR_TOKEN
```

---

### **12. Confirm Appointment** ✅ (Patient only)
```bash
PATCH http://localhost:8000/api/v1/appointments/{APPOINTMENT_ID}/confirm
Authorization: Bearer YOUR_PATIENT_TOKEN
```

---

### **13. Cancel Appointment** ✅ (Patient or Doctor)
```bash
PATCH http://localhost:8000/api/v1/appointments/{APPOINTMENT_ID}/cancel
Authorization: Bearer YOUR_TOKEN
```

---

### **14. Complete Appointment** ✅ (Doctor only)
```bash
PATCH http://localhost:8000/api/v1/appointments/{APPOINTMENT_ID}/complete
Authorization: Bearer YOUR_DOCTOR_TOKEN
Content-Type: application/json

{
  "notes": "Patient recovered well. Prescribed medication."
}
```

---

### **15. Get Doctor Statistics** ✅
```bash
GET http://localhost:8000/api/v1/appointments/stats/doctor/{DOCTOR_ID}?groupBy=month&limit=6
Authorization: Bearer YOUR_TOKEN
```

**Query Parameters:**
- `groupBy`: `month` or `day` (default: `month`)
- `limit`: Number of periods (default: `10`)

**Expected Response:**
```json
{
  "doctorId": "...",
  "totalAppointments": 45,
  "stats": [
    {
      "period": "2025-11",
      "total": 20,
      "completed": 15,
      "cancelled": 3,
      "no_show": 2,
      "scheduled": 0,
      "confirmed": 0
    }
  ]
}
```

---

## 📱 Twilio Webhook Route

### **16. Twilio Webhook (SMS Commands)** ✅
**Note:** This is called by Twilio, not directly by users.

```bash
POST http://localhost:8000/api/v1/twilio/webhook
Content-Type: application/x-www-form-urlencoded
X-Twilio-Signature: <Twilio signature>

Body=CONFIRM 673a1234567890abcdef
From=+919876543210
To=+919908134804
```

**Valid Commands:**
- `CONFIRM <appointment_id>`
- `CANCEL <appointment_id>`

---

## 🧪 Testing Scenarios

### **Scenario 1: Complete Patient Journey**
1. Patient signs up → Get access token
2. Patient logs in → Verify token works
3. Get current profile → Check patient details
4. Get doctor slots → Pick available time
5. Create appointment → Save appointment ID
6. Confirm appointment via SMS command (or PATCH)
7. Get appointment details → Verify status
8. Cancel appointment → Check cancellation

---

### **Scenario 2: Doctor Workflow**
1. Doctor logs in → Get doctor token
2. Get own appointments → See scheduled appointments
3. Patient creates appointment with this doctor
4. Doctor sees new appointment in list
5. Doctor completes appointment with notes
6. Check doctor statistics → Verify counts

---

### **Scenario 3: Error Testing**

#### **Test 1: Duplicate Email**
```bash
POST /api/v1/auth/patient/signup
{
  "email": "john.doe@example.com",  # Same email as before
  ...
}
```
**Expected:** `400 Bad Request` - Email already registered

---

#### **Test 2: Invalid Login**
```bash
POST /api/v1/auth/patient/login
{
  "email": "john.doe@example.com",
  "password": "WrongPassword"
}
```
**Expected:** `401 Unauthorized` - Invalid credentials

---

#### **Test 3: Double Booking**
```bash
# Create first appointment
POST /api/v1/appointments
{
  "doctorId": "DOCTOR_ID",
  "start": "2025-11-18T10:00:00",
  ...
}

# Try to create second appointment at same time
POST /api/v1/appointments
{
  "doctorId": "SAME_DOCTOR_ID",
  "start": "2025-11-18T10:00:00",
  ...
}
```
**Expected:** `409 Conflict` - Time slot not available

---

#### **Test 4: Unauthorized Access**
```bash
# Try to access appointments without token
GET /api/v1/appointments
```
**Expected:** `401 Unauthorized` - Not authenticated

---

#### **Test 5: Invalid Appointment Time**
```bash
POST /api/v1/appointments
{
  "doctorId": "DOCTOR_ID",
  "start": "2025-11-18T10:15:00",  # Not 30-min aligned
  ...
}
```
**Expected:** `400 Bad Request` - Invalid slot alignment

---

## 📊 Using Swagger UI (Easiest Method)

1. Open: `http://localhost:8000/docs`
2. Click on any endpoint to expand
3. Click "Try it out"
4. For authenticated routes:
   - Click "Authorize" button (top right)
   - Enter: `Bearer YOUR_ACCESS_TOKEN`
   - Click "Authorize"
5. Fill in request body/parameters
6. Click "Execute"
7. See response below

---

## 🔧 Using curl (Command Line)

### Patient Signup:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/patient/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "fullName": "Test User",
    "email": "test@example.com",
    "password": "Test123!",
    "phone": "+919999999999",
    "dateOfBirth": "1995-01-01",
    "gender": "male"
  }'
```

### Get Appointments (with auth):
```bash
curl -X GET "http://localhost:8000/api/v1/appointments" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🚀 Quick Test Script

Run this in PowerShell to test basic flow:

```powershell
# 1. Patient signup
$signup = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/patient/signup" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{
    "fullName": "Quick Test User",
    "email": "quicktest@example.com",
    "password": "Test123!",
    "phone": "+919191919191",
    "dateOfBirth": "1995-01-01",
    "gender": "male"
  }'

$token = $signup.accessToken
Write-Host "Token: $token"

# 2. Get profile
$profile = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/users/me" `
  -Method Get `
  -Headers @{"Authorization" = "Bearer $token"}

Write-Host "User: $($profile.fullName)"

# 3. Get time
$time = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/time/now" `
  -Method Get

Write-Host "Server time: $($time.utc)"
```

---

## ✅ Checklist

- [ ] Patient signup works
- [ ] Patient login works
- [ ] Doctor login works
- [ ] Token refresh works
- [ ] Get user profile works
- [ ] Update user profile works
- [ ] Photo upload works
- [ ] Get doctor slots works
- [ ] Create appointment works
- [ ] Get appointments list works
- [ ] Get single appointment works
- [ ] Confirm appointment works
- [ ] Cancel appointment works
- [ ] Complete appointment works (doctor)
- [ ] Get doctor stats works
- [ ] Get server time works
- [ ] Error handling works (401, 400, 409)

---

## 🎯 Key Testing Tips

1. **Always check response status codes** - 200/201 for success, 400/401/409 for errors
2. **Save tokens** - You'll need them for authenticated requests
3. **Use valid doctor IDs** - Run seed script first or get from doctor login
4. **Test permissions** - Patients can't complete appointments, doctors can't confirm
5. **Check Socket.IO events** - Real-time updates should emit on changes
6. **Verify auto-cancel** - Create appointment, wait 15 min past start time
7. **Test reminder scheduling** - Create appointment 4+ hours in future

---

**Need help?** Check logs in terminal where uvicorn is running!
