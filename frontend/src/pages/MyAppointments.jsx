import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { appointmentAPI } from '../services/api'
import { Calendar, Clock, CheckCircle, XCircle, AlertCircle, Check, X } from 'lucide-react'
import { format } from 'date-fns'
import styles from './MyAppointments.module.css'

export default function MyAppointments() {
  const { user } = useAuth()
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [confirmingId, setConfirmingId] = useState(null)
  const [cancellingId, setCancellingId] = useState(null)

  useEffect(() => {
    if (user) {
      fetchAppointments()
    }
  }, [user])

  const fetchAppointments = async () => {
    try {
      const { data } = await appointmentAPI.list({ role: user.role, limit: 100 })
      setAppointments(data || [])
    } catch (error) {
      console.error('Failed to fetch appointments:', error)
      alert('Failed to load appointments. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleConfirm = async (id) => {
    setConfirmingId(id)
    try {
      await appointmentAPI.confirm(id)
      // Update local state immediately for instant feedback
      setAppointments(prev => prev.map(apt => 
        apt._id === id ? { ...apt, status: 'confirmed' } : apt
      ))
      alert('✅ Appointment confirmed successfully!')
    } catch (error) {
      console.error('Failed to confirm appointment:', error)
      alert('❌ Failed to confirm appointment. Please try again.')
    } finally {
      setConfirmingId(null)
    }
  }

  const handleCancel = async (id) => {
    if (!window.confirm('Are you sure you want to cancel this appointment?')) return
    
    setCancellingId(id)
    try {
      await appointmentAPI.cancel(id)
      // Update local state immediately
      setAppointments(prev => prev.map(apt => 
        apt._id === id ? { ...apt, status: 'cancelled' } : apt
      ))
      alert('✅ Appointment cancelled successfully!')
    } catch (error) {
      console.error('Failed to cancel appointment:', error)
      alert('❌ Failed to cancel appointment. Please try again.')
    } finally {
      setCancellingId(null)
    }
  }

  const handleComplete = async (id) => {
    try {
      await appointmentAPI.complete(id)
      fetchAppointments()
    } catch (error) {
      console.error('Failed to complete appointment:', error)
    }
  }

  // Check if appointment is within 3-hour confirmation window
  const isWithinConfirmWindow = (appointmentStart) => {
    const now = new Date()
    const startTime = new Date(appointmentStart)
    const threeHoursBefore = new Date(startTime.getTime() - (3 * 60 * 60 * 1000))
    
    // Confirmation window: 3 hours before to appointment time
    return now >= threeHoursBefore && now < startTime
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

  const filteredAppointments = filter === 'all' 
    ? appointments 
    : appointments.filter(a => a.status === filter)

  if (loading) {
    return <div className={styles.loading}>Loading appointments...</div>
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>My Appointments</h1>
        <p>View and manage all your appointments</p>
      </div>

      <div className={styles.filters}>
        <button 
          className={filter === 'all' ? styles.filterActive : ''}
          onClick={() => setFilter('all')}
        >
          All ({appointments.length})
        </button>
        <button 
          className={filter === 'scheduled' ? styles.filterActive : ''}
          onClick={() => setFilter('scheduled')}
        >
          Scheduled ({appointments.filter(a => a.status === 'scheduled').length})
        </button>
        <button 
          className={filter === 'confirmed' ? styles.filterActive : ''}
          onClick={() => setFilter('confirmed')}
        >
          Confirmed ({appointments.filter(a => a.status === 'confirmed').length})
        </button>
        <button 
          className={filter === 'completed' ? styles.filterActive : ''}
          onClick={() => setFilter('completed')}
        >
          Completed ({appointments.filter(a => a.status === 'completed').length})
        </button>
      </div>

      {filteredAppointments.length === 0 ? (
        <div className={styles.emptyState}>
          <Calendar size={64} color="#cbd5e1" />
          <p>No appointments found</p>
        </div>
      ) : (
        <div className={styles.appointmentGrid}>
          {filteredAppointments.map((appointment) => (
            <div key={appointment._id} className={styles.appointmentCard}>
              <div className={styles.cardHeader}>
                <div className={styles.statusBadge}>
                  {getStatusIcon(appointment.status)}
                  <span className={styles[appointment.status]}>
                    {appointment.status.replace('_', ' ')}
                  </span>
                </div>
                <div className={styles.date}>
                  {format(new Date(appointment.start), 'MMM dd, yyyy')}
                </div>
              </div>

              <div className={styles.cardBody}>
                <div className={styles.timeInfo}>
                  <Clock size={18} />
                  <span>
                    {format(new Date(appointment.start), 'h:mm a')} - 
                    {format(new Date(appointment.end), 'h:mm a')}
                  </span>
                </div>
                
                <div className={styles.reason}>
                  <strong>Reason:</strong> {appointment.reason}
                </div>

                {appointment.reminder3hSent && (
                  <div className={styles.reminderSent}>
                    ✓ Reminder sent
                  </div>
                )}
              </div>

              <div className={styles.cardActions}>
                {/* Patient actions */}
                {user.role === 'patient' && appointment.status === 'scheduled' && (
                  <>
                    {isWithinConfirmWindow(appointment.start) ? (
                      <>
                        <button 
                          onClick={() => handleConfirm(appointment._id)}
                          className={styles.btnConfirm}
                          disabled={confirmingId === appointment._id}
                        >
                          <Check size={16} />
                          {confirmingId === appointment._id ? 'Confirming...' : 'Confirm Now'}
                        </button>
                        <div className={styles.confirmNote}>
                          ⏰ Confirm within 2:45 hours or appointment will be auto-cancelled
                        </div>
                      </>
                    ) : (
                      <div className={styles.waitingConfirm}>
                        ⏳ Confirm button will appear 3 hours before appointment
                      </div>
                    )}
                    <button 
                      onClick={() => handleCancel(appointment._id)}
                      className={styles.btnCancel}
                      disabled={cancellingId === appointment._id}
                    >
                      <X size={16} />
                      {cancellingId === appointment._id ? 'Cancelling...' : 'Cancel'}
                    </button>
                  </>
                )}

                {user.role === 'patient' && appointment.status === 'confirmed' && (
                  <>
                    <div className={styles.confirmedBadge}>
                      <CheckCircle size={18} />
                      Appointment Confirmed ✓
                    </div>
                    <button 
                      onClick={() => handleCancel(appointment._id)}
                      className={styles.btnCancel}
                      disabled={cancellingId === appointment._id}
                    >
                      <X size={16} />
                      Cancel
                    </button>
                  </>
                )}

                {/* Doctor actions */}
                {user.role === 'doctor' && appointment.status === 'confirmed' && (
                  <button 
                    onClick={() => handleComplete(appointment._id)}
                    className={styles.btnComplete}
                  >
                    <Check size={16} />
                    Mark Complete
                  </button>
                )}

                {user.role === 'doctor' && appointment.status === 'scheduled' && (
                  <div className={styles.doctorNote}>
                    Waiting for patient confirmation
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
