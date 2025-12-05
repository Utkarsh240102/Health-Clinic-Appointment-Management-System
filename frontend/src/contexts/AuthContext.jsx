import { createContext, useState, useContext, useEffect } from 'react'
import { authAPI, userAPI } from '../services/api'

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        const { data } = await userAPI.getProfile()
        setUser(data)
      } catch (error) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }
    }
    setLoading(false)
  }

  const login = async (email, password, role = 'patient') => {
    try {
      const loginFn = role === 'doctor' ? authAPI.doctorLogin : authAPI.patientLogin
      const { data } = await loginFn({ email, password })
      
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      
      const { data: userData } = await userAPI.getProfile()
      setUser(userData)
      
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      }
    }
  }

  const signup = async (signupData) => {
    try {
      const { data } = await authAPI.patientSignup(signupData)
      
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      
      const { data: userData } = await userAPI.getProfile()
      setUser(userData)
      
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Signup failed'
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }

  const updateUser = (userData) => {
    setUser(userData)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, updateUser }}>
      {!loading && children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
