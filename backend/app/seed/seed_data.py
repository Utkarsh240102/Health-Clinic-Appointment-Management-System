"""
Seed database with test data:
- 10 doctors with distinct specializations
- 100+ patients
- 500+ appointments (past and future)
"""
import asyncio
import json
from datetime import datetime, timedelta
import random
from faker import Faker
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.core.security import hash_password
from pathlib import Path

fake = Faker()

# Doctor specializations
SPECIALIZATIONS = [
    "Cardiology",
    "Dermatology",
    "Neurology",
    "Pediatrics",
    "Orthopedics",
    "Psychiatry",
    "Radiology",
    "General Practice",
    "Oncology",
    "Gastroenterology"
]

# Appointment reasons
REASONS = [
    "Regular checkup",
    "Follow-up consultation",
    "Annual physical exam",
    "Symptoms evaluation",
    "Medication review",
    "Test results discussion",
    "Specialist consultation",
    "Vaccination",
    "Preventive care",
    "Health screening"
]


async def create_doctors(db, count=10):
    """Create doctor accounts with credentials"""
    import os
    users_collection = db["users"]
    doctors = []
    credentials = []
    
    print(f"\n📝 Creating {count} doctors...")
    
    for i in range(count):
        name = f"Dr. {fake.first_name()} {fake.last_name()}"
        # Read credentials from environment variables (more secure)
        email = os.getenv(f"DOCTOR_{i+1}_EMAIL", f"doctor{i+1}@clinic.com")
        password = os.getenv(f"DOCTOR_{i+1}_PASSWORD", f"Doctor{i+1}Pass")
        phone = f"+1555010{i:04d}"
        
        # Mix of morning and evening schedules
        if i % 3 == 0:
            # Morning only (9am-12pm)
            schedule = [{"weekday": j, "start": "09:00", "end": "12:00"} for j in range(5)]
        elif i % 3 == 1:
            # Afternoon only (2pm-5pm)
            schedule = [{"weekday": j, "start": "14:00", "end": "17:00"} for j in range(5)]
        else:
            # Full day (9am-5pm)
            schedule = [{"weekday": j, "start": "09:00", "end": "17:00"} for j in range(5)]
        
        doctor_doc = {
            "role": "doctor",
            "name": name,
            "email": email,
            "phone": phone,
            "passwordHash": hash_password(password),
            "photoUrl": f"https://i.pravatar.cc/150?u={email}",
            "createdAt": datetime.utcnow(),
            "doctorProfile": {
                "specialization": SPECIALIZATIONS[i % len(SPECIALIZATIONS)],
                "slotDurationMin": 30,
                "weeklySchedule": schedule
            }
        }
        
        result = await users_collection.insert_one(doctor_doc)
        doctor_id = str(result.inserted_id)
        doctors.append(doctor_id)
        
        credentials.append({
            "name": name,
            "email": email,
            "password": password,
            "specialization": doctor_doc["doctorProfile"]["specialization"]
        })
        
        print(f"  ✅ {name} ({doctor_doc['doctorProfile']['specialization']})")
    
    return doctors, credentials


async def create_patients(db, count=100):
    """Create patient accounts"""
    users_collection = db["users"]
    patients = []
    
    print(f"\n📝 Creating {count} patients...")
    
    for i in range(count):
        name = fake.name()
        email = f"patient{i+1}@email.com"
        phone = f"+1555020{i:04d}"
        
        patient_doc = {
            "role": "patient",
            "name": name,
            "email": email,
            "phone": phone,
            "passwordHash": hash_password(f"Patient{i+1}Pass"),
            "photoUrl": f"https://i.pravatar.cc/150?u={email}",
            "createdAt": datetime.utcnow(),
            "patientProfile": {
                "age": random.randint(18, 85),
                "gender": random.choice(["male", "female", "other"]),
                "notes": fake.sentence() if random.random() > 0.7 else None
            }
        }
        
        result = await users_collection.insert_one(patient_doc)
        patients.append(str(result.inserted_id))
    
    print(f"  ✅ Created {count} patients")
    
    return patients


async def create_appointments(db, doctors, patients, target_count=500):
    """Create appointments ensuring no conflicts"""
    appointments_collection = db["appointments"]
    appointments_created = 0
    appointments_by_doctor = {doc: 0 for doc in doctors}
    
    print(f"\n📝 Creating ~{target_count} appointments...")
    
    now = datetime.utcnow()
    
    # 70% in past 6 months, 30% in next 30 days
    past_count = int(target_count * 0.7)
    future_count = target_count - past_count
    
    statuses = ["completed", "cancelled", "no_show"]
    
    # Create past appointments
    for i in range(past_count):
        doctor_id = random.choice(doctors)
        patient_id = random.choice(patients)
        
        # Random date in past 6 months
        days_ago = random.randint(1, 180)
        base_date = now - timedelta(days=days_ago)
        
        # Random slot during working hours
        hour = random.choice([9, 10, 11, 14, 15, 16])
        minute = random.choice([0, 30])
        start = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Skip weekends
        if start.weekday() >= 5:
            continue
        
        end = start + timedelta(minutes=30)
        
        appointment_doc = {
            "doctorId": doctor_id,
            "patientId": patient_id,
            "start": start,
            "end": end,
            "status": random.choice(statuses),
            "reason": random.choice(REASONS),
            "createdAt": start - timedelta(days=random.randint(1, 7)),
            "createdBy": "patient",
            "reminder3hSent": True,
            "twilioLogs": []
        }
        
        try:
            await appointments_collection.insert_one(appointment_doc)
            appointments_created += 1
            appointments_by_doctor[doctor_id] += 1
        except Exception:
            # Conflict, skip
            pass
    
    print(f"  ✅ Created {appointments_created} past appointments")
    
    # Create future appointments
    future_created = 0
    for i in range(future_count):
        doctor_id = random.choice(doctors)
        patient_id = random.choice(patients)
        
        # Random date in next 30 days
        days_ahead = random.randint(1, 30)
        base_date = now + timedelta(days=days_ahead)
        
        # Random slot
        hour = random.choice([9, 10, 11, 14, 15, 16])
        minute = random.choice([0, 30])
        start = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Skip weekends
        if start.weekday() >= 5:
            continue
        
        end = start + timedelta(minutes=30)
        
        # Mix of scheduled and confirmed
        status = "confirmed" if random.random() > 0.5 else "scheduled"
        
        appointment_doc = {
            "doctorId": doctor_id,
            "patientId": patient_id,
            "start": start,
            "end": end,
            "status": status,
            "reason": random.choice(REASONS),
            "createdAt": now - timedelta(days=random.randint(0, 5)),
            "createdBy": "patient",
            "reminder3hSent": False,
            "twilioLogs": []
        }
        
        try:
            await appointments_collection.insert_one(appointment_doc)
            appointments_created += 1
            appointments_by_doctor[doctor_id] += 1
            future_created += 1
        except Exception:
            # Conflict, skip
            pass
    
    print(f"  ✅ Created {future_created} future appointments")
    print(f"  📊 Total: {appointments_created} appointments")
    
    # Check each doctor has minimum appointments
    min_per_doctor = min(appointments_by_doctor.values())
    max_per_doctor = max(appointments_by_doctor.values())
    print(f"  📊 Appointments per doctor: {min_per_doctor} to {max_per_doctor}")
    
    return appointments_created, appointments_by_doctor


async def generate_report(db, doctors, patients, appointments_count, appointments_by_doctor, credentials):
    """Generate seed report"""
    print("\n📄 Generating report...")
    
    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "summary": {
            "doctors": len(doctors),
            "patients": len(patients),
            "appointments": appointments_count
        },
        "doctors_min_appointments": min(appointments_by_doctor.values()),
        "doctors_max_appointments": max(appointments_by_doctor.values()),
        "validation": {
            "all_doctors_have_min_20_appointments": min(appointments_by_doctor.values()) >= 20,
            "at_least_100_patients": len(patients) >= 100
        }
    }
    
    # Save report
    seed_dir = Path(__file__).parent
    report_path = seed_dir / "report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"  ✅ Report saved to {report_path}")
    
    # Save credentials
    credentials_path = seed_dir / "credentials_doctors.json"
    with open(credentials_path, "w") as f:
        json.dump(credentials, f, indent=2)
    
    print(f"  ✅ Credentials saved to {credentials_path}")
    
    return report


async def main():
    """Main seed function"""
    print("=" * 60)
    print("🌱 SEEDING CLINIC DATABASE")
    print("=" * 60)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    # Clear existing data (optional - comment out to preserve)
    print("\n🗑️  Clearing existing data...")
    await db["users"].delete_many({"role": {"$in": ["doctor", "patient"]}})
    await db["appointments"].delete_many({})
    await db["twilio_logs"].delete_many({})
    print("  ✅ Data cleared")
    
    # Create indexes
    print("\n🔧 Creating indexes...")
    from app.models import initialize_indexes
    await initialize_indexes(db)
    
    # Seed data
    doctors, credentials = await create_doctors(db, count=10)
    patients = await create_patients(db, count=100)
    appointments_count, appointments_by_doctor = await create_appointments(
        db, doctors, patients, target_count=500
    )
    
    # Generate report
    report = await generate_report(
        db, doctors, patients, appointments_count, appointments_by_doctor, credentials
    )
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ SEEDING COMPLETE!")
    print("=" * 60)
    print(f"  Doctors:      {report['summary']['doctors']}")
    print(f"  Patients:     {report['summary']['patients']}")
    print(f"  Appointments: {report['summary']['appointments']}")
    print(f"  Min per doctor: {report['doctors_min_appointments']}")
    print(f"  Max per doctor: {report['doctors_max_appointments']}")
    print("\n  ✅ All validation checks passed!" if all(report['validation'].values()) else "  ⚠️  Some validation checks failed")
    print("\n  📁 Check app/seed/credentials_doctors.json for login credentials")
    print("=" * 60)
    
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
