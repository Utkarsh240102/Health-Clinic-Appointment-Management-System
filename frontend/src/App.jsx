import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { useAuth } from './contexts/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import PatientSignup from './pages/PatientSignup'
import Dashboard from './pages/Dashboard'
import BookAppointment from './pages/BookAppointment'
import MyAppointments from './pages/MyAppointments'
import Profile from './pages/Profile'

function PrivateRoute({ children }) {
  const { user } = useAuth()
  return user ? children : <Navigate to="/login" />
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<PatientSignup />} />
          
          <Route path="/" element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }>
            <Route index element={<Dashboard />} />
            <Route path="book" element={<BookAppointment />} />
            <Route path="appointments" element={<MyAppointments />} />
            <Route path="profile" element={<Profile />} />
          </Route>
          
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
