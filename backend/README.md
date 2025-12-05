# Clinic Management System - Backend

FastAPI-based backend for a comprehensive clinic management system with appointment scheduling, real-time notifications, and SMS reminders via Twilio.

## Features

- 🔐 **JWT Authentication** - Separate flows for doctors (login only) and patients (signup + login)
- 📅 **Appointment Booking** - 30-minute slots with conflict detection via partial unique indexes
- ⏰ **Smart Reminders** - 3-hour advance SMS reminders via Twilio
- 🚫 **Auto No-Show Detection** - Automatic cancellation 15 minutes after appointment start
- 🔄 **Real-time Updates** - Socket.IO for live dashboard updates
- 📊 **Analytics** - Appointment statistics and trends
- 🗄️ **MongoDB** - Async Motor client for persistent storage
- 🧪 **Comprehensive Tests** - Unit and integration tests with pytest

## Tech Stack

- **Framework**: FastAPI + Uvicorn (async)
- **Database**: MongoDB with Motor (async driver)
- **Auth**: JWT (PyJWT) + Passlib (bcrypt)
- **Scheduler**: APScheduler with MongoDB jobstore
- **SMS**: Twilio SDK
- **Real-time**: python-socketio (ASGI)
- **Testing**: pytest + httpx

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   ├── core/
│   │   ├── db.py              # MongoDB connection
│   │   ├── jwt.py             # JWT helpers
│   │   └── security.py        # Auth & password hashing
│   ├── models/                # MongoDB models (to be added)
│   ├── schemas/               # Pydantic schemas (to be added)
│   ├── services/              # Business logic (to be added)
│   ├── routes/                # API routes (to be added)
│   ├── utils/                 # Utilities (to be added)
│   ├── seed/                  # Seed data scripts (to be added)
│   └── tests/                 # Test suite (to be added)
├── requirements.txt
├── .env.example
└── README.md
```

## Prerequisites

- Python 3.10+
- MongoDB 4.4+ (replica set recommended for transactions)
- Twilio account (for SMS functionality)
- ngrok (for local Twilio webhook testing)

## Installation

1. **Clone the repository** (or navigate to backend directory)

2. **Create virtual environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Set up MongoDB**
   - Install MongoDB locally or use MongoDB Atlas
   - For transactions support, configure as replica set:
     ```powershell
     mongod --replSet rs0
     # In mongo shell:
     rs.initiate()
     ```

5. **Configure environment variables**
   ```powershell
   cp .env.example .env
   # Edit .env with your actual values
   ```

6. **Required environment variables**:
   - `MONGODB_URL`: MongoDB connection string
   - `JWT_SECRET_KEY`: Secret key for JWT (generate with: `openssl rand -hex 32`)
   - `TWILIO_ACCOUNT_SID`: From Twilio console
   - `TWILIO_AUTH_TOKEN`: From Twilio console
   - `TWILIO_FROM_PATIENT`: Twilio phone number for patient messages
   - `TWILIO_FROM_DOCTOR`: Twilio phone number for doctor messages

## Running the Application

### Development Server

```powershell
uvicorn app.main:socket_app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Ngrok for Twilio Webhooks (Development)

Twilio needs a public URL to send webhook requests. Use ngrok to expose your local server:

```powershell
# Install ngrok from https://ngrok.com/
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`) and configure it in your Twilio console:
- Go to Phone Numbers → Your Number → Messaging
- Set webhook URL to: `https://abc123.ngrok.io/api/v1/twilio/webhook`

## Database Indexes

Critical indexes will be created automatically on startup:
- `users.email` - Unique index
- `users.phone` - Unique index  
- `appointments.{doctorId, start}` - Partial unique index where `status` in ["scheduled", "confirmed"]

## Running Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/unit/test_auth.py

# Run with verbose output
pytest -v
```

## Seeding Data

```powershell
# Run seed script (to be implemented)
python -m app.seed.seed_data

# This will create:
# - 10 doctors with credentials
# - 100+ patients  
# - 500+ appointments
# - Report saved to /seed/report.json
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/patient/signup` - Patient registration
- `POST /api/v1/auth/patient/login` - Patient login
- `POST /api/v1/auth/doctor/login` - Doctor login (seeded accounts only)
- `POST /api/v1/auth/refresh` - Refresh access token

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PATCH /api/v1/users/me` - Update profile
- `POST /api/v1/users/me/photo` - Upload profile photo

### Appointments
- `POST /api/v1/appointments` - Book appointment
- `GET /api/v1/appointments` - List appointments (with filters)
- `GET /api/v1/appointments/:id` - Get appointment details
- `PATCH /api/v1/appointments/:id/confirm` - Confirm appointment
- `PATCH /api/v1/appointments/:id/cancel` - Cancel appointment
- `PATCH /api/v1/appointments/:id/complete` - Mark as completed (doctor)
- `GET /api/v1/appointments/stats/doctor/:id` - Doctor statistics

### Doctors
- `GET /api/v1/doctors/:id/slots` - Get available/booked slots for a date

### System
- `GET /api/v1/time/now` - Get server UTC time (for clock sync)
- `POST /api/v1/twilio/webhook` - Twilio SMS webhook (internal)

## Key Business Rules

1. **Doctors cannot signup** - Only login with pre-seeded accounts
2. **30-minute appointments** - All appointments exactly 30 minutes
3. **No double-booking** - Enforced via partial unique index
4. **3-hour reminders** - SMS sent 3 hours before appointment start
5. **Auto no-show** - Appointments marked no-show 15 minutes after start if not completed
6. **UTC storage** - All times stored in UTC; clients sync via `/time/now`

## Architecture Decisions

- **Async everywhere**: FastAPI + Motor for full async/await support
- **No ORM**: Direct MongoDB operations with Pydantic for validation
- **Partial indexes**: Prevent double-booking only for active appointments
- **Persistent scheduler**: MongoDB jobstore ensures reminders survive restarts
- **Socket.IO**: Real-time bi-directional communication for live updates

## Development Workflow

1. Install dependencies and configure `.env`
2. Start MongoDB (with replica set if using transactions)
3. Run FastAPI dev server with `--reload`
4. (Optional) Start ngrok for Twilio webhook testing
5. Run tests with pytest
6. Use `/docs` for interactive API testing

## Production Considerations

- Use gunicorn/uvicorn workers for production
- Configure managed MongoDB (Atlas) with replica set
- Use Redis + RQ for job queue at scale
- Store uploads in S3/cloud storage
- Set up proper logging and monitoring
- Use environment-specific configs
- Enable rate limiting at reverse proxy level
- Implement token revocation list (Redis)

## Troubleshooting

**MongoDB connection fails**:
- Ensure MongoDB is running: `mongod --version`
- Check connection string in `.env`

**Scheduler not persisting jobs**:
- Verify `SCHEDULER_JOBSTORE_URL` in `.env`
- Check MongoDB permissions

**Twilio webhook not working**:
- Verify ngrok is running and forwarding to port 8000
- Check webhook URL in Twilio console
- Verify Twilio credentials in `.env`

**Tests failing**:
- Ensure test database is separate from dev database
- Check MongoDB is running
- Install all test dependencies

## License

Proprietary - Clinic Management System

## Support

For issues and questions, refer to the project documentation or contact the development team.
