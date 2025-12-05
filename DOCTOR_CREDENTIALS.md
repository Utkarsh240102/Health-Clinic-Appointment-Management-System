# 🔐 Doctor Credentials Security Guide

## Overview
Doctor credentials are now stored securely in the `.env` file instead of being hardcoded in JSON files or source code.

## Current Doctor Accounts

### Login Credentials (Stored in .env)
All credentials are stored as environment variables in `backend/.env` file:

| Doctor # | Email | Password (Env Var) |
|----------|-------|-------------------|
| 1 | doctor1@clinic.com | `DOCTOR_1_PASSWORD` |
| 2 | doctor2@clinic.com | `DOCTOR_2_PASSWORD` |
| 3 | doctor3@clinic.com | `DOCTOR_3_PASSWORD` |
| 4 | doctor4@clinic.com | `DOCTOR_4_PASSWORD` |
| 5 | doctor5@clinic.com | `DOCTOR_5_PASSWORD` |
| 6 | doctor6@clinic.com | `DOCTOR_6_PASSWORD` |
| 7 | doctor7@clinic.com | `DOCTOR_7_PASSWORD` |
| 8 | doctor8@clinic.com | `DOCTOR_8_PASSWORD` |
| 9 | doctor9@clinic.com | `DOCTOR_9_PASSWORD` |
| 10 | doctor10@clinic.com | `DOCTOR_10_PASSWORD` |

### Specializations
The seeding script automatically assigns these specializations:
1. **Cardiology** - Heart and cardiovascular system
2. **Dermatology** - Skin conditions
3. **Neurology** - Nervous system disorders
4. **Pediatrics** - Children's health
5. **Orthopedics** - Bones and joints
6. **Psychiatry** - Mental health
7. **Radiology** - Medical imaging
8. **General Practice** - Primary care
9. **Oncology** - Cancer treatment
10. **Gastroenterology** - Digestive system

## Security Measures Implemented

### ✅ What's Secured:
1. **Environment Variables**
   - All credentials stored in `.env` file
   - `.env` file excluded from git (in `.gitignore`)
   - Never committed to version control

2. **Credential Files**
   - `credentials_doctors.json` added to `.gitignore`
   - `report.json` added to `.gitignore`
   - These files generated during seeding but not tracked

3. **Template File**
   - `.env.example` provides template without real credentials
   - Safe to commit to git
   - Developers copy it to `.env` and fill in real values

### 🔒 Password Storage in Database:
- Passwords are **hashed** using bcrypt before storing
- Plain text passwords never stored in database
- Only used during initial seeding, then discarded

## How It Works

### 1. Development Setup
```bash
# Copy template
cp backend/.env.example backend/.env

# Edit .env and set your own passwords
nano backend/.env
```

### 2. Seeding Database
```bash
cd backend
python -m app.seed.seed_data
```

The script reads credentials from environment variables:
- `DOCTOR_1_EMAIL` and `DOCTOR_1_PASSWORD`
- `DOCTOR_2_EMAIL` and `DOCTOR_2_PASSWORD`
- etc.

### 3. Login to Application
Users login with the email/password from `.env`:
```
Email: doctor1@clinic.com
Password: [value from DOCTOR_1_PASSWORD in .env]
```

## Files Modified

### ✅ Secured Files:
- `backend/.env` - Contains actual credentials (git-ignored)
- `backend/.env.example` - Template without secrets (safe to commit)
- `backend/.gitignore` - Excludes sensitive files
- `backend/app/seed/seed_data.py` - Reads from environment variables

### 🚫 Files Excluded from Git:
- `backend/.env` - Real environment variables
- `backend/app/seed/credentials_doctors.json` - Generated credentials report
- `backend/app/seed/report.json` - Seeding summary report

## Best Practices

### ✅ DO:
- Store credentials in `.env` file
- Use strong, unique passwords for production
- Keep `.env` file private (never share or commit)
- Use different passwords for different environments
- Rotate passwords periodically
- Use environment-specific `.env` files (`.env.production`, `.env.staging`)

### 🚫 DON'T:
- Don't commit `.env` file to git
- Don't share `.env` file via email/chat
- Don't use default passwords in production
- Don't hardcode credentials in source code
- Don't reuse passwords across environments

## Production Deployment

### For Production Environment:
1. **Create `.env.production`**
   ```bash
   cp .env.example .env.production
   ```

2. **Use Strong Passwords**
   - Minimum 16 characters
   - Mix of uppercase, lowercase, numbers, symbols
   - Use password manager to generate

3. **Environment Variables on Server**
   ```bash
   # Option 1: Use .env file
   export $(cat .env.production | xargs)
   
   # Option 2: Set directly
   export DOCTOR_1_PASSWORD="SuperSecurePassword123!@#"
   
   # Option 3: Use secrets manager (AWS, Azure, etc.)
   ```

4. **Restrict File Permissions**
   ```bash
   chmod 600 .env.production
   ```

## Access Control

### Current Setup (Development):
- **10 Doctor accounts** with credentials in `.env`
- All have standard email format: `doctor{N}@clinic.com`
- Passwords: Stored as environment variables

### Recommended Production Setup:
1. **Create real doctor accounts** with verified emails
2. **Implement password reset** flow for forgotten passwords
3. **Add two-factor authentication** for doctors
4. **Use OAuth/SSO** if integrating with hospital systems
5. **Audit logging** for all credential changes

## Troubleshooting

### Issue: Seeding fails with "No password found"
**Solution**: Check `.env` file has `DOCTOR_{N}_PASSWORD` variables set

### Issue: Can't login after seeding
**Solution**: Verify the password in `.env` matches what you're entering

### Issue: Credentials file still in git
**Solution**: 
```bash
# Remove from git history
git rm --cached backend/app/seed/credentials_doctors.json
git commit -m "Remove credentials from git"
```

## Viewing Current Credentials

### Safe Method (without exposing in terminal history):
```python
# In Python shell
import os
from dotenv import load_dotenv

load_dotenv()

# Print doctor 1 credentials
print(f"Email: {os.getenv('DOCTOR_1_EMAIL')}")
print(f"Password: {os.getenv('DOCTOR_1_PASSWORD')}")
```

### Quick View:
```bash
# In backend directory
grep "DOCTOR_" .env
```

## Rotating Passwords

To change doctor passwords:

1. **Update .env file**
   ```bash
   nano backend/.env
   # Change DOCTOR_1_PASSWORD=NewPassword123!
   ```

2. **Re-seed database** OR **Update in database**:
   ```python
   # Option A: Re-seed (wipes all data)
   python -m app.seed.seed_data
   
   # Option B: Update specific doctor (preserves data)
   from app.core.security import hash_password
   from app.core.db import get_users_collection
   import asyncio
   
   async def update_password():
       users = get_users_collection()
       await users.update_one(
           {"email": "doctor1@clinic.com"},
           {"$set": {"passwordHash": hash_password("NewPassword123!")}}
       )
   
   asyncio.run(update_password())
   ```

## Additional Security Recommendations

1. **Rate Limiting**: Implement login attempt limits
2. **Session Management**: Auto-logout after inactivity
3. **Audit Logs**: Track all login attempts
4. **Password Policies**: Enforce complexity requirements
5. **MFA**: Add multi-factor authentication
6. **Encryption**: Encrypt `.env` file at rest (production)
7. **Secrets Manager**: Use AWS Secrets Manager, Azure Key Vault, etc.

## Summary

✅ **All doctor credentials now stored securely in `.env` file**
✅ **Credentials excluded from git via `.gitignore`**
✅ **Template file (`.env.example`) provided for new developers**
✅ **Passwords hashed with bcrypt before storage**
✅ **No sensitive data in source code**

**Current Passwords:** Check `backend/.env` file (not committed to git)
