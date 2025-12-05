# Quick Test: Book Appointment Endpoint
# Run this after the backend is running

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

# Step 1: Create a test patient and login
print("=" * 60)
print("STEP 1: Patient Signup")
print("=" * 60)

signup_data = {
    "fullName": "Test Patient",
    "email": "testpatient@example.com",
    "password": "TestPass123!",
    "phone": "+919876543210",
    "dateOfBirth": "1995-05-15",
    "gender": "male",
    "address": "123 Test Street"
}

try:
    response = requests.post(f"{BASE_URL}/auth/patient/signup", json=signup_data)
    if response.status_code == 201:
        data = response.json()
        patient_token = data["accessToken"]
        patient_id = data["user"]["id"]
        print(f"✅ Patient created successfully!")
        print(f"   Email: {data['user']['email']}")
        print(f"   Token: {patient_token[:50]}...")
    elif response.status_code == 400 and "already registered" in response.text:
        print("⚠️  Patient already exists, trying to login...")
        # Login instead
        login_response = requests.post(f"{BASE_URL}/auth/patient/login", json={
            "email": signup_data["email"],
            "password": signup_data["password"]
        })
        if login_response.status_code == 200:
            data = login_response.json()
            patient_token = data["accessToken"]
            patient_id = data["user"]["id"]
            print(f"✅ Patient logged in successfully!")
            print(f"   Token: {patient_token[:50]}...")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            exit(1)
    else:
        print(f"❌ Signup failed: {response.status_code}")
        print(response.text)
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Step 2: Login as doctor to get doctor ID
print("\n" + "=" * 60)
print("STEP 2: Doctor Login")
print("=" * 60)

doctor_login_data = {
    "email": "doctor1@clinic.com",
    "password": "Doctor1Pass"
}

try:
    response = requests.post(f"{BASE_URL}/auth/doctor/login", json=doctor_login_data)
    if response.status_code == 200:
        data = response.json()
        doctor_token = data["accessToken"]
        doctor_id = data["user"]["id"]
        doctor_name = data["user"]["fullName"]
        specialization = data["user"]["doctorProfile"]["specialization"]
        print(f"✅ Doctor logged in successfully!")
        print(f"   Name: {doctor_name}")
        print(f"   Specialization: {specialization}")
        print(f"   Doctor ID: {doctor_id}")
    else:
        print(f"❌ Doctor login failed: {response.status_code}")
        print(response.text)
        print("\n💡 TIP: Run the seed script first:")
        print("   python -m app.seed.seed_data")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 Make sure the backend is running!")
    exit(1)

# Step 3: Get available slots for doctor
print("\n" + "=" * 60)
print("STEP 3: Get Doctor Available Slots")
print("=" * 60)

# Get tomorrow's date
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
print(f"📅 Checking slots for: {tomorrow}")

headers = {"Authorization": f"Bearer {patient_token}"}

try:
    response = requests.get(
        f"{BASE_URL}/doctors/{doctor_id}/slots",
        params={"date": tomorrow},
        headers=headers
    )
    if response.status_code == 200:
        slots = response.json()
        available_slots = [slot for slot in slots if slot["available"]]
        print(f"✅ Found {len(available_slots)} available slots")
        
        if available_slots:
            print("\n📋 First 5 available slots:")
            for i, slot in enumerate(available_slots[:5], 1):
                print(f"   {i}. {slot['start']} - {slot['end']}")
            
            # Pick first available slot
            selected_slot = available_slots[0]["start"]
            print(f"\n✨ Selected slot: {selected_slot}")
        else:
            print("⚠️  No available slots found!")
            print("💡 Try a different date or doctor")
            exit(1)
    else:
        print(f"❌ Failed to get slots: {response.status_code}")
        print(response.text)
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Step 4: Book the appointment
print("\n" + "=" * 60)
print("STEP 4: Book Appointment")
print("=" * 60)

appointment_data = {
    "doctorId": doctor_id,
    "start": selected_slot,
    "reason": "Regular checkup - Testing booking endpoint"
}

print(f"📝 Booking details:")
print(f"   Doctor: {doctor_name}")
print(f"   Time: {selected_slot}")
print(f"   Reason: {appointment_data['reason']}")
print()

try:
    response = requests.post(
        f"{BASE_URL}/appointments",
        json=appointment_data,
        headers=headers
    )
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 201:
        data = response.json()
        print("\n" + "🎉" * 30)
        print("✅ APPOINTMENT BOOKED SUCCESSFULLY!")
        print("🎉" * 30)
        print(f"\n📋 Appointment Details:")
        print(f"   ID: {data['id']}")
        print(f"   Status: {data['status']}")
        print(f"   Start: {data['start']}")
        print(f"   Doctor: {data['doctorName']}")
        print(f"   Patient: {data['patientName']}")
        print(f"   Reason: {data['reason']}")
        
        if data.get("reminderJobMeta"):
            print(f"\n⏰ Reminder scheduled:")
            print(f"   Job ID: {data['reminderJobMeta']['job_id']}")
            print(f"   Will send at: {data['reminderJobMeta']['scheduled_at']}")
        
        appointment_id = data['id']
        
        # Step 5: Verify we can retrieve the appointment
        print("\n" + "=" * 60)
        print("STEP 5: Verify Appointment (Get by ID)")
        print("=" * 60)
        
        response = requests.get(
            f"{BASE_URL}/appointments/{appointment_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Successfully retrieved appointment")
            data = response.json()
            print(f"   Status: {data['status']}")
            print(f"   Doctor: {data['doctorName']}")
        else:
            print(f"⚠️  Failed to retrieve: {response.status_code}")
        
        # Step 6: Test confirming the appointment
        print("\n" + "=" * 60)
        print("STEP 6: Confirm Appointment")
        print("=" * 60)
        
        response = requests.patch(
            f"{BASE_URL}/appointments/{appointment_id}/confirm",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Appointment confirmed!")
            print(f"   Status: {data['status']}")
        else:
            print(f"⚠️  Failed to confirm: {response.status_code}")
            print(response.text)
            
    elif response.status_code == 409:
        print("\n❌ BOOKING FAILED: Time slot not available")
        print("💡 This slot may already be booked. Try a different time.")
        
    elif response.status_code == 400:
        print("\n❌ BOOKING FAILED: Invalid request")
        print("💡 Check the error message above for details.")
        
    elif response.status_code == 401:
        print("\n❌ BOOKING FAILED: Unauthorized")
        print("💡 Token may be invalid or expired.")
        
    else:
        print(f"\n❌ BOOKING FAILED: Unexpected error")
        
except Exception as e:
    print(f"❌ Error during booking: {e}")
    exit(1)

# Summary
print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("✅ Patient signup/login - SUCCESS")
print("✅ Doctor login - SUCCESS")
print("✅ Get available slots - SUCCESS")
print(f"✅ Book appointment - {'SUCCESS' if response.status_code == 201 else 'FAILED'}")
print("\n💡 Check your terminal running uvicorn for backend logs!")
