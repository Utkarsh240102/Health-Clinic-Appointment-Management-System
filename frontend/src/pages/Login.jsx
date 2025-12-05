import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Calendar, Mail, Lock, AlertCircle } from 'lucide-react'
import styles from './Auth.module.css'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('patient')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const result = await login(email, password, role)
    
    if (result.success) {
      navigate('/')
    } else {
      setError(result.error)
    }
    
    setLoading(false)
  }

  return (
    <div className={styles.authContainer}>
      <div className={styles.authCard}>
        <div className={styles.authHeader}>
          <Calendar size={48} className={styles.authIcon} />
          <h1>Clinic Management System</h1>
          <p>Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.authForm}>
          <div className={styles.roleToggle}>
            <button
              type="button"
              className={role === 'patient' ? styles.roleActive : ''}
              onClick={() => setRole('patient')}
            >
              Patient
            </button>
            <button
              type="button"
              className={role === 'doctor' ? styles.roleActive : ''}
              onClick={() => setRole('doctor')}
            >
              Doctor
            </button>
          </div>

          {error && (
            <div className={styles.error}>
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}

          <div className={styles.inputGroup}>
            <Mail size={20} />
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className={styles.inputGroup}>
            <Lock size={20} />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className={styles.submitBtn} disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>

          {role === 'patient' && (
            <p className={styles.switchAuth}>
              Don't have an account? <Link to="/signup">Sign up</Link>
            </p>
          )}
        </form>
      </div>
    </div>
  )
}
