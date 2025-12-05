import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Calendar, Mail, Lock, User, Phone, AlertCircle } from 'lucide-react'
import styles from './Auth.module.css'

export default function PatientSignup() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  const { signup } = useAuth()
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }

    setLoading(true)

    const result = await signup({
      name: formData.name,
      email: formData.email,
      phone: formData.phone.startsWith('+') ? formData.phone : `+${formData.phone}`,
      password: formData.password
    })
    
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
          <h1>Patient Registration</h1>
          <p>Create your account</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.authForm}>
          {error && (
            <div className={styles.error}>
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}

          <div className={styles.inputGroup}>
            <User size={20} />
            <input
              type="text"
              name="name"
              placeholder="Full Name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>

          <div className={styles.inputGroup}>
            <Mail size={20} />
            <input
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className={styles.inputGroup}>
            <Phone size={20} />
            <input
              type="tel"
              name="phone"
              placeholder="Phone (+1234567890)"
              value={formData.phone}
              onChange={handleChange}
              required
            />
          </div>

          <div className={styles.inputGroup}>
            <Lock size={20} />
            <input
              type="password"
              name="password"
              placeholder="Password (min 6 characters)"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          <div className={styles.inputGroup}>
            <Lock size={20} />
            <input
              type="password"
              name="confirmPassword"
              placeholder="Confirm Password"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
            />
          </div>

          <button type="submit" className={styles.submitBtn} disabled={loading}>
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>

          <p className={styles.switchAuth}>
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
