# 🚀 Quick Start Guide - Running Backend & Frontend

## Prerequisites

- **Python 3.10+** installed
- **Node.js 18+** and npm installed
- **MongoDB** running on `mongodb://localhost:27017`

---

## Backend Setup & Run

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment (First Time Only)
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies (First Time Only)
```bash
pip install -r requirements.txt
```

### 5. Setup Environment Variables (First Time Only)
```bash
# Copy template
cp .env.example .env

# Edit .env file with your credentials
# Make sure MongoDB, Twilio, and JWT settings are correct
```

### 6. Seed Database (First Time Only)
```bash
python -m app.seed.seed_data
```

### 7. Run Backend Server
```bash
uvicorn app.main:app --reload
```

**Backend will run on:** `http://localhost:8000`

---

## Frontend Setup & Run

### 1. Navigate to Frontend Directory (New Terminal)
```bash
cd frontend
```

### 2. Install Dependencies (First Time Only)
```bash
npm install
```

### 3. Run Frontend Development Server
```bash
npm run dev
```

**Frontend will run on:** `http://localhost:5173`

---

## Quick Commands (After Initial Setup)

### Start Backend
```bash
# From project root
cd backend
.\venv\Scripts\Activate.ps1  # Windows PowerShell
uvicorn app.main:app --reload
```

### Start Frontend
```bash
# From project root (new terminal)
cd frontend
npm run dev
```

---

## One-Line Commands (Windows PowerShell)

### Backend
```powershell
cd backend; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload
```

### Frontend
```powershell
cd frontend; npm run dev
```

---

## Running Both Simultaneously

### Option 1: Two Separate Terminals

**Terminal 1 (Backend):**
```bash
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

### Option 2: Background Process (PowerShell)

**Start Backend in Background:**
```powershell
cd backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload"
cd ..
```

**Start Frontend:**
```powershell
cd frontend
npm run dev
```

---

## Verifying It's Running

### Check Backend
Open: `http://localhost:8000/docs`
- Should see FastAPI Swagger documentation

### Check Frontend
Open: `http://localhost:5173`
- Should see the login page

### Test Login
- **Doctor Login:**
  - Email: `doctor1@clinic.com`
  - Password: Check `backend/.env` file for `DOCTOR_1_PASSWORD` (default: `Doctor1Pass`)

- **Patient Signup:**
  - Create a new patient account from the signup page

---

## Stopping the Servers

### Stop Backend
Press `CTRL + C` in the backend terminal

### Stop Frontend
Press `CTRL + C` in the frontend terminal

---

## Troubleshooting

### Backend Won't Start

**Issue:** `ModuleNotFoundError`
```bash
# Activate venv and reinstall
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Issue:** `ValidationError` for environment variables
```bash
# Check .env file exists and has all required fields
cd backend
cat .env
```

**Issue:** `Connection refused` (MongoDB)
```bash
# Make sure MongoDB is running
# Start MongoDB service or run mongod
```

### Frontend Won't Start

**Issue:** `command not found: npm`
```bash
# Install Node.js from https://nodejs.org/
```

**Issue:** Dependencies missing
```bash
cd frontend
npm install
```

**Issue:** Port 5173 already in use
```bash
# Kill process on port 5173 or use different port
npm run dev -- --port 3000
```

### Can't Login

**Issue:** Network error / Can't connect to backend
- Make sure backend is running on `http://localhost:8000`
- Check browser console for errors

**Issue:** Invalid credentials
- For doctors: Check password in `backend/.env` file
- For patients: Make sure you've signed up first

---

## Development Workflow

### 1. Start Development
```bash
# Terminal 1: Backend
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 2. Access Application
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### 3. Make Changes
- Backend changes auto-reload (thanks to `--reload` flag)
- Frontend changes auto-reload (Vite HMR)

---

## Production Build

### Backend
```bash
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run build
npm run preview
```

---

## Environment Variables

### Backend (.env)
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=clinic_db
JWT_SECRET_KEY=your-secret-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
# ... (see .env.example for full list)
```

### Frontend (vite.config.js)
```javascript
// API proxy configured in vite.config.js
// All /api requests proxied to http://localhost:8000
```

---

## Useful Commands

### Backend
```bash
# Run tests
pytest

# Run specific test
pytest app/tests/test_auth.py

# Check Python version
python --version

# List installed packages
pip list

# Seed database with test data
python -m app.seed.seed_data
```

### Frontend
```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Check for dependency updates
npm outdated

# Run linter (if configured)
npm run lint
```

---

## Default Ports

| Service | Port | URL |
|---------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| Frontend Dev | 5173 | http://localhost:5173 |
| MongoDB | 27017 | mongodb://localhost:27017 |
| API Docs | 8000 | http://localhost:8000/docs |

---

## Next Steps

1. ✅ Start backend and frontend
2. ✅ Create a patient account (signup)
3. ✅ Login as doctor (use credentials from .env)
4. ✅ Book an appointment as patient
5. ✅ View appointments in dashboard
6. ✅ Test SMS reminders (if Twilio configured)

---

## Need Help?

- **Backend Docs:** `http://localhost:8000/docs`
- **Doctor Credentials:** Check `DOCTOR_CREDENTIALS.md`
- **API Reference:** Check `backend/README.md`
- **Frontend Features:** Check `frontend/README.md`

**Happy Coding! 🚀**
