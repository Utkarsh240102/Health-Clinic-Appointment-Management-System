import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { LogOut, Calendar, CalendarPlus, User, Home } from 'lucide-react'
import styles from './Layout.module.css'

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className={styles.layout}>
      <nav className={styles.nav}>
        <div className={styles.navContainer}>
          <div className={styles.navBrand}>
            <Calendar size={32} />
            <span>Clinic System</span>
          </div>
          
          <div className={styles.navLinks}>
            <NavLink to="/" className={({ isActive }) => 
              isActive ? `${styles.navLink} ${styles.active}` : styles.navLink
            }>
              <Home size={20} />
              <span>Dashboard</span>
            </NavLink>
            
            {user?.role === 'patient' && (
              <NavLink to="/book" className={({ isActive }) => 
                isActive ? `${styles.navLink} ${styles.active}` : styles.navLink
              }>
                <CalendarPlus size={20} />
                <span>Book Appointment</span>
              </NavLink>
            )}
            
            <NavLink to="/appointments" className={({ isActive }) => 
              isActive ? `${styles.navLink} ${styles.active}` : styles.navLink
            }>
              <Calendar size={20} />
              <span>My Appointments</span>
            </NavLink>
            
            <NavLink to="/profile" className={({ isActive }) => 
              isActive ? `${styles.navLink} ${styles.active}` : styles.navLink
            }>
              <User size={20} />
              <span>Profile</span>
            </NavLink>
          </div>
          
          <div className={styles.navUser}>
            <span className={styles.userName}>{user?.name}</span>
            <span className={styles.userRole}>{user?.role}</span>
            <button onClick={handleLogout} className={styles.logoutBtn}>
              <LogOut size={20} />
            </button>
          </div>
        </div>
      </nav>
      
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  )
}
