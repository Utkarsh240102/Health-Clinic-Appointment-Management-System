# 🔐 Quick Reference - Doctor Login Credentials

> **⚠️ IMPORTANT**: This file is for development reference only. 
> In production, use strong unique passwords and never commit this file to git.

## Current Doctor Accounts (Development)

All credentials are stored in `backend/.env` file.

### Login Information

| # | Name | Email | Password (in .env) | Specialization |
|---|------|-------|-------------------|----------------|
| 1 | Various* | doctor1@clinic.com | `DOCTOR_1_PASSWORD=Doctor1Pass` | Cardiology |
| 2 | Various* | doctor2@clinic.com | `DOCTOR_2_PASSWORD=Doctor2Pass` | Dermatology |
| 3 | Various* | doctor3@clinic.com | `DOCTOR_3_PASSWORD=Doctor3Pass` | Neurology |
| 4 | Various* | doctor4@clinic.com | `DOCTOR_4_PASSWORD=Doctor4Pass` | Pediatrics |
| 5 | Various* | doctor5@clinic.com | `DOCTOR_5_PASSWORD=Doctor5Pass` | Orthopedics |
| 6 | Various* | doctor6@clinic.com | `DOCTOR_6_PASSWORD=Doctor6Pass` | Psychiatry |
| 7 | Various* | doctor7@clinic.com | `DOCTOR_7_PASSWORD=Doctor7Pass` | Radiology |
| 8 | Various* | doctor8@clinic.com | `DOCTOR_8_PASSWORD=Doctor8Pass` | General Practice |
| 9 | Various* | doctor9@clinic.com | `DOCTOR_9_PASSWORD=Doctor9Pass` | Oncology |
| 10 | Various* | doctor10@clinic.com | `DOCTOR_10_PASSWORD=Doctor10Pass` | Gastroenterology |

\* Doctor names are randomly generated during seeding using Faker library

## Quick Login Examples

### For Testing/Development:

**Cardiologist:**
```
Email: doctor1@clinic.com
Password: Doctor1Pass
```

**Dermatologist:**
```
Email: doctor2@clinic.com
Password: Doctor2Pass
```

**General Practitioner:**
```
Email: doctor8@clinic.com
Password: Doctor8Pass
```

## How to View Current Passwords

### Option 1: Check .env file directly
```bash
cd backend
cat .env | grep DOCTOR_
```

### Option 2: Use Python
```python
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

for i in range(1, 11):
    email = os.getenv(f'DOCTOR_{i}_EMAIL')
    password = os.getenv(f'DOCTOR_{i}_PASSWORD')
    print(f"Doctor {i}: {email} / {password}")
```

## Working Hours

Doctors have different schedules:
- **Doctors 1, 4, 7, 10**: Morning only (9:00 AM - 12:00 PM)
- **Doctors 2, 5, 8**: Afternoon only (2:00 PM - 5:00 PM)  
- **Doctors 3, 6, 9**: Full day (9:00 AM - 5:00 PM)

All doctors work **Monday - Friday** only (no weekends).

## Features by Doctor Role

When logged in as doctor, you can:
- ✅ View dashboard with appointment statistics
- ✅ See all your appointments
- ✅ View patient details for your appointments
- ✅ Mark appointments as completed
- ✅ Cancel appointments
- ✅ Update your profile
- ✅ View your specialization and schedule

## Changing Passwords

### For Development:
1. Edit `backend/.env` file
2. Change the `DOCTOR_X_PASSWORD` value
3. Re-seed database: `python -m app.seed.seed_data`

### For Production:
See `DOCTOR_CREDENTIALS.md` for secure password rotation procedures.

## Security Reminders

🔒 **DO:**
- Keep `.env` file private
- Use different passwords for production
- Store `.env` in secure location
- Rotate passwords regularly

🚫 **DON'T:**
- Don't commit `.env` to git (already in `.gitignore`)
- Don't share passwords via email/chat
- Don't use development passwords in production
- Don't reuse passwords

## Troubleshooting

**Can't login with doctor credentials?**
1. Check `backend/.env` has the password
2. Verify database was seeded: `python -m app.seed.seed_data`
3. Check password matches exactly (case-sensitive)
4. Verify backend server is running

**Need to reset all doctor passwords?**
```bash
cd backend
python -m app.seed.seed_data  # Re-seeds entire database
```

## Files Location

- **Credentials**: `backend/.env` (git-ignored)
- **Template**: `backend/.env.example` (safe to commit)
- **Seed Script**: `backend/app/seed/seed_data.py`
- **Documentation**: `DOCTOR_CREDENTIALS.md`

---

**Last Updated**: When you run the seed script
**Total Doctors**: 10
**Default Password Pattern**: `Doctor{N}Pass` where N is 1-10
