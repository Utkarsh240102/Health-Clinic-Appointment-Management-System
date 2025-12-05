# Clinic Management System - Frontend

A modern, responsive React frontend for the Clinic Management System.

## Features

### 🔐 Authentication
- **Patient Signup**: Register new patient accounts
- **Login System**: Separate login for patients and doctors
- **JWT Authentication**: Secure token-based authentication with auto-refresh

### 📅 Appointment Management
- **Book Appointments**: Patients can schedule appointments with doctors
- **View Appointments**: See all your appointments with status
- **Filter Appointments**: Filter by status (scheduled, confirmed, completed, etc.)
- **Confirm/Cancel**: Manage appointment status
- **Complete Appointments**: Doctors can mark appointments as complete

### 👤 Profile Management
- **View Profile**: See your account information
- **Edit Profile**: Update name and phone number
- **Upload Photo**: Add or change profile picture
- **Doctor Info**: View specialization and schedule (for doctors)

### 📊 Dashboard
- **Statistics**: View appointment counts and status breakdown (for doctors)
- **Recent Appointments**: Quick view of latest appointments
- **Role-based UI**: Different views for patients and doctors

## Tech Stack

- **React 18** - UI library
- **React Router v6** - Navigation and routing
- **Axios** - HTTP client with interceptors
- **Vite** - Build tool and dev server
- **CSS Modules** - Scoped styling
- **date-fns** - Date formatting
- **lucide-react** - Modern icon library

## Installation

### Prerequisites
- Node.js 18+ and npm
- Backend server running on http://localhost:8000

### Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Access the application**
   ```
   http://localhost:5173
   ```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout.jsx              # Main layout with navigation
│   │   └── Layout.module.css
│   ├── contexts/
│   │   └── AuthContext.jsx         # Authentication context
│   ├── pages/
│   │   ├── Login.jsx               # Login page
│   │   ├── PatientSignup.jsx       # Patient registration
│   │   ├── Dashboard.jsx           # Dashboard with stats
│   │   ├── BookAppointment.jsx     # Book appointment form
│   │   ├── MyAppointments.jsx      # Appointments list
│   │   ├── Profile.jsx             # User profile
│   │   └── *.module.css            # Page-specific styles
│   ├── services/
│   │   └── api.js                  # API client with interceptors
│   ├── App.jsx                     # Main app component
│   ├── main.jsx                    # Entry point
│   └── index.css                   # Global styles
├── index.html
├── vite.config.js
└── package.json
```

## Features by Role

### Patient Features
✅ Sign up and create account
✅ Login to existing account
✅ Book appointments with doctors
✅ View all appointments
✅ Confirm scheduled appointments
✅ Cancel appointments
✅ Update profile information
✅ Upload profile photo

### Doctor Features
✅ Login to account
✅ View dashboard with statistics
✅ See all appointments
✅ View appointment details
✅ Mark appointments as complete
✅ Cancel appointments
✅ Update profile information
✅ View specialization and schedule

## API Integration

All API calls go through `src/services/api.js` which includes:
- Automatic token attachment
- Token refresh on 401 errors
- Centralized error handling
- Request/response interceptors

### Endpoints Used
- `/api/v1/auth/patient/signup` - Patient registration
- `/api/v1/auth/patient/login` - Patient login
- `/api/v1/auth/doctor/login` - Doctor login
- `/api/v1/auth/refresh` - Token refresh
- `/api/v1/users/me` - Get/update profile
- `/api/v1/users/me/photo` - Upload photo
- `/api/v1/appointments` - CRUD operations
- `/api/v1/appointments/:id/confirm` - Confirm appointment
- `/api/v1/appointments/:id/cancel` - Cancel appointment
- `/api/v1/appointments/:id/complete` - Complete appointment

## Development

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## Test Credentials

### Doctor Accounts
**Note**: Doctor credentials are securely stored in the backend `.env` file. Check `DOCTOR_CREDENTIALS.md` for details.

Default development credentials:
- Email: `doctor1@clinic.com` - Password: Check `backend/.env` file (`DOCTOR_1_PASSWORD`)
- Email: `doctor2@clinic.com` - Password: Check `backend/.env` file (`DOCTOR_2_PASSWORD`)
- _10 doctors total available (doctor1 through doctor10)_

### Patient Accounts
- Sign up to create a new patient account

### 🔒 Security Note
All credentials are stored in environment variables (`.env` file) which is git-ignored for security. Never commit credentials to version control.

## Notes

- Make sure the backend server is running on port 8000
- The app uses proxy configuration in vite.config.js for API calls
- All times are displayed in local timezone
- Appointments must be booked in 30-minute slots (when validation is enabled)
- Photos are uploaded and stored on the backend

## Troubleshooting

**Issue**: Can't connect to backend
- **Solution**: Ensure backend is running on http://localhost:8000

**Issue**: Login fails
- **Solution**: Check network tab for errors, verify credentials

**Issue**: Token expired
- **Solution**: Token auto-refreshes, if it fails completely, logout and login again

**Issue**: Appointments not loading
- **Solution**: Check browser console for errors, verify API is accessible

## Future Enhancements

- Real-time notifications via WebSocket
- Doctor availability calendar
- Patient medical history
- Prescription management
- Video consultation integration
- Email notifications
- Advanced search and filters
- Export appointment data
