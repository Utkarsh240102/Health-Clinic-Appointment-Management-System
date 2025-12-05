import { useState, useEffect } from 'react'
import { appointmentAPI, userAPI } from '../services/api'
import { Calendar, Clock, User, FileText, AlertCircle, CheckCircle } from 'lucide-react'
import { format } from 'date-fns'
import styles from './BookAppointment.module.css'

export default function BookAppointment() {
  const [doctors, setDoctors] = useState([])
  const [selectedDoctor, setSelectedDoctor] = useState('')
  const [appointmentDate, setAppointmentDate] = useState('')
  const [availableSlots, setAvailableSlots] = useState([])
  const [selectedSlot, setSelectedSlot] = useState(null)
  const [reason, setReason] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingSlots, setLoadingSlots] = useState(false)
  const [message, setMessage] = useState(null)

  useEffect(() => {
    fetchDoctors()
  }, [])

  useEffect(() => {
    if (selectedDoctor && appointmentDate) {
      fetchAvailableSlots()
    } else {
      setAvailableSlots([])
      setSelectedSlot(null)
    }
  }, [selectedDoctor, appointmentDate])

  const fetchDoctors = async () => {
    try {
      const { data } = await userAPI.getDoctors()
      setDoctors(data)
    } catch (error) {
      console.error('Failed to fetch doctors:', error)
      setMessage({ 
        type: 'error', 
        text: 'Failed to load doctors list' 
      })
    }
  }

  const fetchAvailableSlots = async () => {
    setLoadingSlots(true)
    setSelectedSlot(null)
    try {
      const { data } = await appointmentAPI.getSlots(selectedDoctor, appointmentDate)
      setAvailableSlots(data)
    } catch (error) {
      console.error('Failed to fetch slots:', error)
      setMessage({ 
        type: 'error', 
        text: 'Failed to load available time slots' 
      })
      setAvailableSlots([])
    } finally {
      setLoadingSlots(false)
    }
  }

  const formatTime = (dateString) => {
    const date = new Date(dateString)
    return format(date, 'HH:mm')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!selectedSlot) {
      setMessage({ type: 'error', text: 'Please select a time slot' })
      return
    }

    setMessage(null)
    setLoading(true)

    try {
      await appointmentAPI.book({
        doctorId: selectedDoctor,
        start: selectedSlot.start,
        end: selectedSlot.end,
        reason
      })

      setMessage({ type: 'success', text: 'Appointment booked successfully!' })
      
      // Reset form
      setSelectedDoctor('')
      setAppointmentDate('')
      setAvailableSlots([])
      setSelectedSlot(null)
      setReason('')
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to book appointment' 
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Book an Appointment</h1>
        <p>Schedule your visit with our healthcare professionals</p>
      </div>

      <div className={styles.card}>
        <form onSubmit={handleSubmit} className={styles.form}>
          {message && (
            <div className={`${styles.message} ${styles[message.type]}`}>
              {message.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
              <span>{message.text}</span>
            </div>
          )}

          <div className={styles.formGroup}>
            <label>
              <User size={20} />
              <span>Select Doctor</span>
            </label>
            <select
              value={selectedDoctor}
              onChange={(e) => setSelectedDoctor(e.target.value)}
              required
              className={styles.select}
            >
              <option value="">Choose a doctor...</option>
              {doctors.map((doctor) => (
                <option key={doctor._id} value={doctor._id}>
                  {doctor.name} - {doctor.doctorProfile?.specialization || 'General'}
                </option>
              ))}
            </select>
          </div>

          <div className={styles.formGroup}>
            <label>
              <Calendar size={20} />
              <span>Date</span>
            </label>
            <input
              type="date"
              value={appointmentDate}
              onChange={(e) => setAppointmentDate(e.target.value)}
              min={format(new Date(), 'yyyy-MM-dd')}
              required
              className={styles.input}
            />
          </div>

          {selectedDoctor && appointmentDate && (
            <div className={styles.formGroup}>
              <label>
                <Clock size={20} />
                <span>Available Time Slots</span>
              </label>
              {loadingSlots ? (
                <div className={styles.loadingSlots}>Loading available slots...</div>
              ) : availableSlots.length > 0 ? (
                <div className={styles.slotsGrid}>
                  {availableSlots.map((slot, index) => (
                    slot.available && (
                      <button
                        key={index}
                        type="button"
                        className={`${styles.slotButton} ${
                          selectedSlot?.start === slot.start ? styles.selected : ''
                        }`}
                        onClick={() => setSelectedSlot(slot)}
                      >
                        {formatTime(slot.start)}
                      </button>
                    )
                  ))}
                </div>
              ) : (
                <div className={styles.noSlots}>
                  No available slots for this date. Please select another date.
                </div>
              )}
            </div>
          )}

          <div className={styles.formGroup}>
            <label>
              <FileText size={20} />
              <span>Reason for Visit</span>
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Describe your symptoms or reason for visit..."
              rows={4}
              required
              className={styles.textarea}
            />
          </div>

          <button 
            type="submit" 
            disabled={loading || !selectedSlot} 
            className={styles.submitBtn}
          >
            {loading ? 'Booking...' : 'Book Appointment'}
          </button>
        </form>
      </div>
    </div>
  )
}
