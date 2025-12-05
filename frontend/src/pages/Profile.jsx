import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { userAPI } from '../services/api'
import { User, Mail, Phone, Camera, AlertCircle, CheckCircle } from 'lucide-react'
import styles from './Profile.module.css'

export default function Profile() {
  const { user, updateUser } = useAuth()
  const [editing, setEditing] = useState(false)
  const [formData, setFormData] = useState({
    name: user?.name || '',
    phone: user?.phone || ''
  })
  const [message, setMessage] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setMessage(null)
    setLoading(true)

    try {
      const { data } = await userAPI.updateProfile(formData)
      updateUser(data)
      setMessage({ type: 'success', text: 'Profile updated successfully!' })
      setEditing(false)
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to update profile' 
      })
    } finally {
      setLoading(false)
    }
  }

  const handlePhotoUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const { data } = await userAPI.uploadPhoto(formData)
      updateUser(data)
      setMessage({ type: 'success', text: 'Photo uploaded successfully!' })
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: 'Failed to upload photo' 
      })
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Profile</h1>
        <p>Manage your account information</p>
      </div>

      <div className={styles.profileCard}>
        {message && (
          <div className={`${styles.message} ${styles[message.type]}`}>
            {message.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
            <span>{message.text}</span>
          </div>
        )}

        <div className={styles.photoSection}>
          <div className={styles.photoWrapper}>
            {user?.photoUrl ? (
              <img src={user.photoUrl} alt={user.name} className={styles.photo} />
            ) : (
              <div className={styles.photoPlaceholder}>
                <User size={48} />
              </div>
            )}
            <label className={styles.photoUpload}>
              <Camera size={20} />
              <input 
                type="file" 
                accept="image/*"
                onChange={handlePhotoUpload}
                hidden
              />
            </label>
          </div>
          <div className={styles.photoInfo}>
            <h2>{user?.name}</h2>
            <p className={styles.role}>{user?.role}</p>
          </div>
        </div>

        {editing ? (
          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.formGroup}>
              <label>
                <User size={20} />
                <span>Full Name</span>
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                className={styles.input}
              />
            </div>

            <div className={styles.formGroup}>
              <label>
                <Phone size={20} />
                <span>Phone</span>
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                required
                className={styles.input}
              />
            </div>

            <div className={styles.formActions}>
              <button 
                type="button" 
                onClick={() => setEditing(false)}
                className={styles.btnCancel}
              >
                Cancel
              </button>
              <button 
                type="submit" 
                disabled={loading}
                className={styles.btnSave}
              >
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        ) : (
          <div className={styles.infoSection}>
            <div className={styles.infoItem}>
              <Mail size={20} />
              <div>
                <span className={styles.infoLabel}>Email</span>
                <span className={styles.infoValue}>{user?.email}</span>
              </div>
            </div>

            <div className={styles.infoItem}>
              <Phone size={20} />
              <div>
                <span className={styles.infoLabel}>Phone</span>
                <span className={styles.infoValue}>{user?.phone}</span>
              </div>
            </div>

            <div className={styles.infoItem}>
              <User size={20} />
              <div>
                <span className={styles.infoLabel}>Full Name</span>
                <span className={styles.infoValue}>{user?.name}</span>
              </div>
            </div>

            {user?.doctorProfile && (
              <div className={styles.doctorInfo}>
                <h3>Doctor Information</h3>
                <p><strong>Specialization:</strong> {user.doctorProfile.specialization}</p>
                <p><strong>Slot Duration:</strong> {user.doctorProfile.slotDurationMin} minutes</p>
              </div>
            )}

            <button 
              onClick={() => setEditing(true)}
              className={styles.btnEdit}
            >
              Edit Profile
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
