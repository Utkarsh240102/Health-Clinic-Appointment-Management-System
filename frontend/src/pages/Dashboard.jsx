import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { appointmentAPI } from '../services/api'
import { Calendar, Clock, CheckCircle, XCircle, AlertCircle, TrendingUp } from 'lucide-react'
import { format } from 'date-fns'
import styles from './Dashboard.module.css'

export default function Dashboard() {
  const { user } = useAuth()
  const [appointments, setAppointments] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [apptResponse] = await Promise.all([
        appointmentAPI.list({ role: user.role, limit: 5 })
      ])
      
      setAppointments(apptResponse.data || [])
      
      // Calculate stats from appointments
      if (user.role === 'doctor' && apptResponse.data) {
        const myAppointments = apptResponse.data
        const stats = {
          total: myAppointments.length,
          scheduled: myAppointments.filter(a => a.status === 'scheduled').length,
          confirmed: myAppointments.filter(a => a.status === 'confirmed').length,
          completed: myAppointments.filter(a => a.status === 'completed').length,
          cancelled: myAppointments.filter(a => a.status === 'cancelled').length,
          no_show: myAppointments.filter(a => a.status === 'no_show').length
        }
        setStats(stats)
      }
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status) => {
    switch(status) {
      case 'scheduled': return <Clock className={styles.iconScheduled} />
      case 'confirmed': return <CheckCircle className={styles.iconConfirmed} />
      case 'completed': return <CheckCircle className={styles.iconCompleted} />
      case 'cancelled': return <XCircle className={styles.iconCancelled} />
      case 'no_show': return <AlertCircle className={styles.iconNoShow} />
      default: return <Clock />
    }
  }

  if (loading) {
    return <div className={styles.loading}>Loading...</div>
  }

  return (
    <div className={styles.dashboard}>
      <div className={styles.header}>
        <h1>Welcome back, {user?.name}! 👋</h1>
        <p className={styles.subtitle}>
          {user?.role === 'doctor' ? 'Manage your appointments and patients' : 'Book and manage your appointments'}
        </p>
      </div>

      {user?.role === 'doctor' && stats && (
        <div className={styles.statsGrid}>
          <div className={styles.statCard}>
            <div className={styles.statIcon} style={{background: '#dbeafe'}}>
              <Calendar size={24} color="#2563eb" />
            </div>
            <div className={styles.statContent}>
              <span className={styles.statValue}>{stats.total}</span>
              <span className={styles.statLabel}>Total Appointments</span>
            </div>
          </div>

          <div className={styles.statCard}>
            <div className={styles.statIcon} style={{background: '#fef3c7'}}>
              <Clock size={24} color="#f59e0b" />
            </div>
            <div className={styles.statContent}>
              <span className={styles.statValue}>{stats.scheduled}</span>
              <span className={styles.statLabel}>Scheduled</span>
            </div>
          </div>

          <div className={styles.statCard}>
            <div className={styles.statIcon} style={{background: '#dcfce7'}}>
              <CheckCircle size={24} color="#16a34a" />
            </div>
            <div className={styles.statContent}>
              <span className={styles.statValue}>{stats.confirmed}</span>
              <span className={styles.statLabel}>Confirmed</span>
            </div>
          </div>

          <div className={styles.statCard}>
            <div className={styles.statIcon} style={{background: '#e0e7ff'}}>
              <TrendingUp size={24} color="#6366f1" />
            </div>
            <div className={styles.statContent}>
              <span className={styles.statValue}>{stats.completed}</span>
              <span className={styles.statLabel}>Completed</span>
            </div>
          </div>
        </div>
      )}

      <div className={styles.section}>
        <h2>Recent Appointments</h2>
        
        {appointments.length === 0 ? (
          <div className={styles.emptyState}>
            <Calendar size={48} color="#cbd5e1" />
            <p>No appointments yet</p>
          </div>
        ) : (
          <div className={styles.appointmentList}>
            {appointments.map((appointment) => (
              <div key={appointment._id} className={styles.appointmentCard}>
                <div className={styles.appointmentHeader}>
                  <div className={styles.appointmentStatus}>
                    {getStatusIcon(appointment.status)}
                    <span className={`${styles.statusBadge} ${styles[appointment.status]}`}>
                      {appointment.status.replace('_', ' ')}
                    </span>
                  </div>
                  <div className={styles.appointmentDate}>
                    {format(new Date(appointment.start), 'MMM dd, yyyy')}
                  </div>
                </div>
                
                <div className={styles.appointmentBody}>
                  <p className={styles.appointmentTime}>
                    <Clock size={16} />
                    {format(new Date(appointment.start), 'h:mm a')} - {format(new Date(appointment.end), 'h:mm a')}
                  </p>
                  <p className={styles.appointmentReason}>{appointment.reason}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
