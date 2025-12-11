# Frontend Documentation - Health Clinic Management System

React-based frontend with responsive design, real-time updates, and intuitive appointment management.

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/           # Reusable components
│   │   ├── Navbar.jsx
│   │   ├── Navbar.module.css
│   │   ├── PrivateRoute.jsx
│   │   └── AppointmentCard.jsx
│   │
│   ├── pages/               # Page components
│   │   ├── Login.jsx
│   │   ├── Login.module.css
│   │   ├── Register.jsx
│   │   ├── Register.module.css
│   │   ├── Dashboard.jsx
│   │   ├── Dashboard.module.css
│   │   ├── BookAppointment.jsx
│   │   ├── BookAppointment.module.css
│   │   ├── MyAppointments.jsx
│   │   └── MyAppointments.module.css
│   │
│   ├── contexts/            # React Context
│   │   └── AuthContext.jsx
│   │
│   ├── services/            # API services
│   │   ├── api.js          # Axios configuration
│   │   ├── auth.js         # Auth API calls
│   │   └── appointments.js # Appointment API calls
│   │
│   ├── utils/              # Helper functions
│   │   └── formatters.js
│   │
│   ├── App.jsx             # Main app component
│   ├── App.css
│   ├── main.jsx            # Entry point
│   └── index.css           # Global styles
│
├── public/
│   └── vite.svg
│
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## 🚀 Setup & Installation

### 1. Install Dependencies

```bash
cd frontend
npm install
```

**Key Dependencies:**
- `react@18.2.0` - UI library
- `react-dom@18.2.0` - DOM rendering
- `react-router-dom@6.20.0` - Routing
- `axios@1.6.2` - HTTP client
- `date-fns@2.30.0` - Date formatting

**Dev Dependencies:**
- `vite@5.0.8` - Build tool
- `@vitejs/plugin-react@4.2.1` - React plugin
- `eslint@8.55.0` - Linting

### 2. Environment Configuration

Create `.env` file in frontend directory:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

**Note:** Vite requires `VITE_` prefix for environment variables.

### 3. Run Development Server

```bash
npm run dev
```

Frontend runs at: `http://localhost:5173`

### 4. Build for Production

```bash
npm run build
```

Output in `dist/` directory.

### 5. Preview Production Build

```bash
npm run preview
```

## 🎨 Component Architecture

### 1. Authentication Context (`src/contexts/AuthContext.jsx`)

Manages global authentication state using React Context API.

**State:**
```javascript
{
  user: {
    id: "507f1f77bcf86cd799439011",
    name: "John Doe",
    email: "john@example.com",
    role: "patient"
  },
  isAuthenticated: true,
  isLoading: false
}
```

**Methods:**
- `login(email, password)` - Authenticate user
- `register(userData)` - Create new account
- `logout()` - Clear session
- `refreshToken()` - Renew access token

**Usage:**
```javascript
import { useAuth } from '../contexts/AuthContext';

function MyComponent() {
  const { user, login, logout } = useAuth();
  
  return (
    <div>
      {user ? (
        <button onClick={logout}>Logout</button>
      ) : (
        <button onClick={() => login(email, password)}>Login</button>
      )}
    </div>
  );
}
```

### 2. Private Route (`src/components/PrivateRoute.jsx`)

Protects routes requiring authentication.

```javascript
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function PrivateRoute({ children, requiredRole }) {
  const { user, isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) return <div>Loading...</div>;
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
}
```

**Usage in Routes:**
```javascript
<Route path="/dashboard" element={
  <PrivateRoute>
    <Dashboard />
  </PrivateRoute>
} />
```

### 3. Navbar Component (`src/components/Navbar.jsx`)

Responsive navigation bar with role-based menu items.

**Features:**
- Logo and app name
- Navigation links (Dashboard, Book, My Appointments)
- User profile dropdown
- Logout button
- Mobile responsive (hamburger menu)

**CSS Modules:**
```css
.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem 2rem;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
}

.navLinks {
  display: flex;
  gap: 2rem;
}
```

### 4. Appointment Card (`src/components/AppointmentCard.jsx`)

Reusable component for displaying appointment details.

**Props:**
```javascript
{
  appointment: {
    id: string,
    doctor: { name, specialization },
    patient: { name, phone },
    start: DateTime,
    end: DateTime,
    status: string,
    reason: string
  },
  onConfirm: (id) => void,
  onCancel: (id) => void,
  showActions: boolean
}
```

**Status Badges:**
```javascript
const statusColors = {
  scheduled: 'bg-yellow-500',
  confirmed: 'bg-green-500',
  completed: 'bg-blue-500',
  cancelled: 'bg-red-500',
  no_show: 'bg-gray-500'
};
```

## 📄 Pages

### 1. Login Page (`src/pages/Login.jsx`)

**Features:**
- Email/phone authentication
- Password visibility toggle
- "Remember me" checkbox
- Link to registration
- Form validation
- Error handling

**State Management:**
```javascript
const [formData, setFormData] = useState({
  email: '',
  password: '',
  rememberMe: false
});
const [error, setError] = useState('');
const [isLoading, setIsLoading] = useState(false);
```

**Form Submission:**
```javascript
const handleSubmit = async (e) => {
  e.preventDefault();
  setError('');
  setIsLoading(true);
  
  try {
    await login(formData.email, formData.password);
    navigate('/dashboard');
  } catch (err) {
    setError(err.response?.data?.detail || 'Login failed');
  } finally {
    setIsLoading(false);
  }
};
```

### 2. Registration Page (`src/pages/Register.jsx`)

**Features:**
- Multi-field form (name, email, phone, password)
- Role selection (doctor/patient)
- Specialization field (for doctors)
- Password strength indicator
- Confirm password validation
- Phone number formatting

**Validation:**
```javascript
const validateForm = () => {
  if (!formData.name.trim()) {
    setError('Name is required');
    return false;
  }
  
  if (!/\S+@\S+\.\S+/.test(formData.email)) {
    setError('Invalid email format');
    return false;
  }
  
  if (formData.password.length < 8) {
    setError('Password must be at least 8 characters');
    return false;
  }
  
  if (formData.password !== formData.confirmPassword) {
    setError('Passwords do not match');
    return false;
  }
  
  return true;
};
```

### 3. Dashboard (`src/pages/Dashboard.jsx`)

**Patient Dashboard:**
- Welcome message with user name
- Quick statistics cards:
  - Total appointments
  - Upcoming appointments
  - Confirmed appointments
  - Completed appointments
- Next 5 upcoming appointments
- Quick action buttons (Book New, View All)

**Doctor Dashboard:**
- Today's appointments list
- Appointment count by status
- Patient information
- Quick status update buttons

**Data Fetching:**
```javascript
useEffect(() => {
  const fetchDashboardData = async () => {
    try {
      const appointments = await appointmentService.getMyAppointments();
      
      const stats = {
        total: appointments.length,
        upcoming: appointments.filter(a => 
          new Date(a.start) > new Date() && 
          a.status !== 'cancelled'
        ).length,
        confirmed: appointments.filter(a => 
          a.status === 'confirmed'
        ).length,
        completed: appointments.filter(a => 
          a.status === 'completed'
        ).length
      };
      
      setStats(stats);
      setUpcoming(appointments
        .filter(a => new Date(a.start) > new Date())
        .sort((a, b) => new Date(a.start) - new Date(b.start))
        .slice(0, 5)
      );
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    }
  };
  
  fetchDashboardData();
}, []);
```

### 4. Book Appointment (`src/pages/BookAppointment.jsx`)

**Features:**
- Doctor selection dropdown with specialization
- Date picker (disables past dates and weekends)
- Available time slots display (30-minute intervals)
- Slot selection (visual feedback)
- Reason for visit textarea
- Real-time validation
- Loading states

**Workflow:**
```
1. Select Doctor → Load doctor details
2. Select Date → Fetch available slots
3. Select Time Slot → Enable booking
4. Enter Reason → Submit form
```

**Fetch Available Slots:**
```javascript
const fetchAvailableSlots = async () => {
  if (!selectedDoctor || !selectedDate) return;
  
  setLoadingSlots(true);
  try {
    const response = await appointmentService.getAvailableSlots(
      selectedDoctor,
      format(selectedDate, 'yyyy-MM-dd')
    );
    setAvailableSlots(response.data.slots);
  } catch (error) {
    console.error('Failed to fetch slots:', error);
    setError('Could not load available slots');
  } finally {
    setLoadingSlots(false);
  }
};
```

**Book Appointment:**
```javascript
const handleBooking = async () => {
  if (!selectedSlot) return;
  
  setIsBooking(true);
  try {
    const appointmentData = {
      doctorId: selectedDoctor,
      start: selectedSlot.start,
      end: selectedSlot.end,
      reason: reason.trim() || 'General consultation'
    };
    
    await appointmentService.createAppointment(appointmentData);
    
    alert('✅ Appointment booked successfully!');
    navigate('/my-appointments');
  } catch (error) {
    setError(error.response?.data?.detail || 'Booking failed');
  } finally {
    setIsBooking(false);
  }
};
```

### 5. My Appointments (`src/pages/MyAppointments.jsx`)

**Features:**
- List of all appointments (past & upcoming)
- Status filtering (all/scheduled/confirmed/completed)
- Appointment details display
- Confirm button (3-hour window, shown when applicable)
- Cancel button
- Loading states with instant feedback
- Success/error alerts
- Confirmed badge display

**State Management:**
```javascript
const [appointments, setAppointments] = useState([]);
const [filteredAppointments, setFilteredAppointments] = useState([]);
const [statusFilter, setStatusFilter] = useState('all');
const [confirmingId, setConfirmingId] = useState(null);
const [cancellingId, setCancellingId] = useState(null);
```

**Confirm Appointment:**
```javascript
const handleConfirm = async (appointmentId) => {
  setConfirmingId(appointmentId);
  
  try {
    await appointmentService.confirmAppointment(appointmentId);
    
    // Instant UI update (optimistic update)
    setAppointments(prev => prev.map(apt => 
      apt.id === appointmentId 
        ? { ...apt, status: 'confirmed' }
        : apt
    ));
    
    alert('✅ Appointment confirmed!');
  } catch (error) {
    console.error('Failed to confirm:', error);
    alert('❌ ' + (error.response?.data?.detail || 'Confirmation failed'));
  } finally {
    setConfirmingId(null);
  }
};
```

**Cancel Appointment:**
```javascript
const handleCancel = async (appointmentId) => {
  if (!confirm('Are you sure you want to cancel this appointment?')) {
    return;
  }
  
  setCancellingId(appointmentId);
  
  try {
    await appointmentService.cancelAppointment(appointmentId);
    
    // Update UI
    setAppointments(prev => prev.map(apt => 
      apt.id === appointmentId 
        ? { ...apt, status: 'cancelled' }
        : apt
    ));
    
    alert('✅ Appointment cancelled');
  } catch (error) {
    console.error('Failed to cancel:', error);
    alert('❌ ' + (error.response?.data?.detail || 'Cancellation failed'));
  } finally {
    setCancellingId(null);
  }
};
```

**Confirm Button Logic:**
```javascript
const canConfirm = (appointment) => {
  if (appointment.status !== 'scheduled') return false;
  
  const appointmentTime = new Date(appointment.start);
  const now = new Date();
  const hoursDiff = (appointmentTime - now) / (1000 * 60 * 60);
  
  // Can confirm if appointment is within 3 hours
  return hoursDiff > 0 && hoursDiff <= 3;
};
```

## 🔌 API Services

### 1. Axios Configuration (`src/services/api.js`)

**Base Setup:**
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor (add auth token)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor (handle errors)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If 401 and haven't retried yet, try refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
          `${api.defaults.baseURL}/auth/refresh`,
          {},
          {
            headers: { Authorization: `Bearer ${refreshToken}` }
          }
        );
        
        const { access_token } = response.data;
        localStorage.setItem('access_token', access_token);
        
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

### 2. Auth Service (`src/services/auth.js`)

```javascript
import api from './api';

export const authService = {
  async login(email, password) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    return response.data;
  },
  
  async register(userData) {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  
  async getCurrentUser() {
    const response = await api.get('/users/me');
    return response.data;
  },
  
  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    const response = await api.post('/auth/refresh', {}, {
      headers: { Authorization: `Bearer ${refreshToken}` }
    });
    return response.data;
  }
};
```

### 3. Appointment Service (`src/services/appointments.js`)

```javascript
import api from './api';

export const appointmentService = {
  async getAllDoctors() {
    const response = await api.get('/users/doctors');
    return response.data;
  },
  
  async getAvailableSlots(doctorId, date) {
    const response = await api.get(`/appointments/slots/${doctorId}`, {
      params: { date }
    });
    return response.data;
  },
  
  async createAppointment(appointmentData) {
    const response = await api.post('/appointments', appointmentData);
    return response.data;
  },
  
  async getMyAppointments() {
    const response = await api.get('/appointments');
    return response.data;
  },
  
  async getAppointmentById(id) {
    const response = await api.get(`/appointments/${id}`);
    return response.data;
  },
  
  async confirmAppointment(id) {
    const response = await api.patch(`/appointments/${id}/confirm`);
    return response.data;
  },
  
  async cancelAppointment(id) {
    const response = await api.patch(`/appointments/${id}/cancel`);
    return response.data;
  }
};
```

## 🎨 Styling

### CSS Modules

Each component has its own scoped CSS file using CSS Modules:

```javascript
// MyAppointments.jsx
import styles from './MyAppointments.module.css';

<div className={styles.container}>
  <h1 className={styles.title}>My Appointments</h1>
</div>
```

**Benefits:**
- Scoped styles (no global conflicts)
- Better organization
- Tree-shaking (unused styles removed)

### Global Styles (`src/index.css`)

```css
:root {
  --primary: #667eea;
  --secondary: #764ba2;
  --success: #10b981;
  --danger: #ef4444;
  --warning: #f59e0b;
  --gray: #6b7280;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.6;
  color: #1f2937;
}
```

### Responsive Design

```css
/* Mobile first approach */
.container {
  padding: 1rem;
}

/* Tablet */
@media (min-width: 768px) {
  .container {
    padding: 2rem;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 3rem;
  }
}
```

## 🔧 Utility Functions (`src/utils/formatters.js`)

```javascript
import { format, parseISO, formatDistanceToNow } from 'date-fns';

export const formatDate = (dateString) => {
  try {
    return format(parseISO(dateString), 'MMM dd, yyyy');
  } catch {
    return 'Invalid date';
  }
};

export const formatTime = (dateString) => {
  try {
    return format(parseISO(dateString), 'hh:mm a');
  } catch {
    return 'Invalid time';
  }
};

export const formatDateTime = (dateString) => {
  try {
    return format(parseISO(dateString), 'MMM dd, yyyy • hh:mm a');
  } catch {
    return 'Invalid date';
  }
};

export const timeUntil = (dateString) => {
  try {
    return formatDistanceToNow(parseISO(dateString), { addSuffix: true });
  } catch {
    return 'Unknown';
  }
};

export const formatPhoneNumber = (phone) => {
  // Format: +1234567890 → +1 (234) 567-890
  if (!phone) return '';
  
  const cleaned = phone.replace(/\D/g, '');
  const match = cleaned.match(/^(\d{1})(\d{3})(\d{3})(\d{4})$/);
  
  if (match) {
    return `+${match[1]} (${match[2]}) ${match[3]}-${match[4]}`;
  }
  
  return phone;
};

export const getStatusColor = (status) => {
  const colors = {
    scheduled: '#f59e0b',   // Yellow
    confirmed: '#10b981',   // Green
    completed: '#3b82f6',   // Blue
    cancelled: '#ef4444',   // Red
    no_show: '#6b7280'      // Gray
  };
  
  return colors[status] || '#6b7280';
};
```

## 🧪 Testing (Future)

### Setup Testing Library

```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest
```

### Sample Test

```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Login from '../pages/Login';

describe('Login Component', () => {
  it('renders login form', () => {
    render(<Login />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });
  
  it('shows error on invalid email', async () => {
    render(<Login />);
    
    const emailInput = screen.getByLabelText(/email/i);
    fireEvent.change(emailInput, { target: { value: 'invalid' } });
    
    const submitButton = screen.getByRole('button', { name: /login/i });
    fireEvent.click(submitButton);
    
    expect(await screen.findByText(/invalid email/i)).toBeInTheDocument();
  });
});
```

## 🚀 Build & Deployment

### Production Build

```bash
npm run build
```

**Output:**
- Optimized bundle in `dist/` directory
- Code splitting
- Minified CSS/JS
- Asset optimization

### Preview Build

```bash
npm run preview
```

### Deploy to Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=dist
```

### Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### Environment Variables (Production)

Set on hosting platform:
```
VITE_API_URL=https://api.yourdomain.com/api/v1
```

## 🐛 Common Issues & Solutions

### Issue 1: "Cannot find module 'date-fns'"

**Solution:**
```bash
npm install date-fns
```

### Issue 2: CORS errors

**Solution:**
- Backend must allow frontend origin
- Check backend CORS configuration
- Verify API URL in .env

### Issue 3: Blank page in production

**Solution:**
- Check browser console for errors
- Verify environment variables set correctly
- Ensure API URL uses HTTPS in production

### Issue 4: Token expired errors

**Solution:**
- Refresh token logic implemented in api.js interceptor
- Clear localStorage and re-login if refresh fails

## 📊 Performance Optimization

### Code Splitting

```javascript
// Lazy load routes
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const BookAppointment = lazy(() => import('./pages/BookAppointment'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/book" element={<BookAppointment />} />
      </Routes>
    </Suspense>
  );
}
```

### Image Optimization

- Use WebP format
- Lazy load images
- Optimize dimensions

### Bundle Size

```bash
# Analyze bundle
npm run build -- --mode analyze
```

## 🔐 Security Best Practices

1. **Never store sensitive data in localStorage** (only tokens)
2. **Validate all inputs** before sending to API
3. **Use HTTPS** in production
4. **Implement CSP headers**
5. **Keep dependencies updated**

```bash
npm audit
npm audit fix
```

## 📱 Progressive Web App (Future)

Add service worker for offline functionality:

```javascript
// vite.config.js
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Health Clinic',
        short_name: 'Clinic',
        description: 'Appointment Management System',
        theme_color: '#667eea'
      }
    })
  ]
});
```

---

**Frontend maintained with ❤️ using React and Vite**
