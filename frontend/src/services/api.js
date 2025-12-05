import axios from 'axios'

const API_URL = 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const { data } = await axios.post(`${API_URL}/auth/refresh`, {
          refresh_token: refreshToken
        })
        
        localStorage.setItem('access_token', data.access_token)
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`
        
        return api(originalRequest)
      } catch (err) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(err)
      }
    }
    
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  patientSignup: (data) => api.post('/auth/patient/signup', data),
  patientLogin: (data) => api.post('/auth/patient/login', data),
  doctorLogin: (data) => api.post('/auth/doctor/login', data),
  refresh: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken })
}

// User API
export const userAPI = {
  getProfile: () => api.get('/users/me'),
  updateProfile: (data) => api.patch('/users/me', data),
  uploadPhoto: (formData) => api.post('/users/me/photo', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getDoctors: () => api.get('/users/doctors')
}

// Appointment API
export const appointmentAPI = {
  book: (data) => api.post('/appointments', data),
  list: (params) => api.get('/appointments', { params }),
  get: (id) => api.get(`/appointments/${id}`),
  confirm: (id) => api.patch(`/appointments/${id}/confirm`),
  cancel: (id) => api.patch(`/appointments/${id}/cancel`),
  complete: (id) => api.patch(`/appointments/${id}/complete`),
  getDoctorStats: (doctorId) => api.get(`/appointments/stats/doctor/${doctorId}`),
  getSlots: (doctorId, date) => api.get(`/appointments/slots/${doctorId}`, { params: { date } })
}

// Time API
export const timeAPI = {
  getNow: () => api.get('/time/now')
}

export default api
