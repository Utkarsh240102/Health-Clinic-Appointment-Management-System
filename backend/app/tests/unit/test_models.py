import pytest
from pydantic import ValidationError
from app.models.user_model import UserModel, DoctorProfile, PatientProfile, WeeklyScheduleSlot
from app.models.appointment_model import AppointmentModel, ReminderJobMeta
from app.models.twilio_log_model import TwilioLogModel
from datetime import datetime, timedelta


class TestUserModel:
    """Test UserModel validation"""
    
    def test_valid_doctor_user(self):
        """Test creating a valid doctor user"""
        user_data = {
            "role": "doctor",
            "name": "Dr. John Smith",
            "email": "john@example.com",
            "phone": "+1234567890",
            "passwordHash": "hashed_password",
            "doctorProfile": {
                "specialization": "Cardiology",
                "slotDurationMin": 30,
                "weeklySchedule": [
                    {"weekday": 0, "start": "09:00", "end": "17:00"}
                ]
            }
        }
        user = UserModel(**user_data)
        assert user.role == "doctor"
        assert user.doctorProfile is not None
        assert user.doctorProfile.specialization == "Cardiology"
    
    def test_valid_patient_user(self):
        """Test creating a valid patient user"""
        user_data = {
            "role": "patient",
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "+0987654321",
            "passwordHash": "hashed_password",
            "patientProfile": {
                "age": 30,
                "gender": "female"
            }
        }
        user = UserModel(**user_data)
        assert user.role == "patient"
        assert user.patientProfile is not None
        assert user.patientProfile.age == 30
    
    def test_invalid_email(self):
        """Test that invalid email raises validation error"""
        user_data = {
            "role": "patient",
            "name": "Test User",
            "email": "invalid-email",
            "phone": "+1234567890",
            "passwordHash": "hashed"
        }
        with pytest.raises(ValidationError):
            UserModel(**user_data)
    
    def test_invalid_phone(self):
        """Test that invalid phone raises validation error"""
        user_data = {
            "role": "patient",
            "name": "Test User",
            "email": "test@example.com",
            "phone": "invalid",
            "passwordHash": "hashed"
        }
        with pytest.raises(ValidationError):
            UserModel(**user_data)
    
    def test_weekly_schedule_validation(self):
        """Test weekly schedule validation"""
        # Valid schedule
        schedule = WeeklyScheduleSlot(weekday=0, start="09:00", end="17:00")
        assert schedule.weekday == 0
        
        # Invalid weekday
        with pytest.raises(ValidationError):
            WeeklyScheduleSlot(weekday=7, start="09:00", end="17:00")
        
        # Invalid time format
        with pytest.raises(ValidationError):
            WeeklyScheduleSlot(weekday=0, start="25:00", end="17:00")


class TestAppointmentModel:
    """Test AppointmentModel validation"""
    
    def test_valid_appointment(self):
        """Test creating a valid appointment"""
        start_time = datetime.utcnow() + timedelta(hours=5)
        end_time = start_time + timedelta(minutes=30)
        
        appointment_data = {
            "doctorId": "doc123",
            "patientId": "pat123",
            "start": start_time,
            "end": end_time,
            "status": "scheduled",
            "reason": "Regular checkup",
            "createdBy": "patient"
        }
        appointment = AppointmentModel(**appointment_data)
        assert appointment.status == "scheduled"
        assert appointment.reminder3hSent is False
    
    def test_invalid_status(self):
        """Test that invalid status raises validation error"""
        appointment_data = {
            "doctorId": "doc123",
            "patientId": "pat123",
            "start": datetime.utcnow(),
            "end": datetime.utcnow() + timedelta(minutes=30),
            "status": "invalid_status",
            "reason": "Checkup",
            "createdBy": "patient"
        }
        with pytest.raises(ValidationError):
            AppointmentModel(**appointment_data)
    
    def test_reason_length_validation(self):
        """Test reason field length validation"""
        # Valid reason
        appointment_data = {
            "doctorId": "doc123",
            "patientId": "pat123",
            "start": datetime.utcnow(),
            "end": datetime.utcnow() + timedelta(minutes=30),
            "reason": "Valid reason",
            "createdBy": "patient"
        }
        appointment = AppointmentModel(**appointment_data)
        assert len(appointment.reason) > 0
        
        # Empty reason should fail
        appointment_data["reason"] = ""
        with pytest.raises(ValidationError):
            AppointmentModel(**appointment_data)
        
        # Too long reason should fail
        appointment_data["reason"] = "x" * 501
        with pytest.raises(ValidationError):
            AppointmentModel(**appointment_data)


class TestTwilioLogModel:
    """Test TwilioLogModel validation"""
    
    def test_valid_twilio_log(self):
        """Test creating a valid Twilio log"""
        log_data = {
            "to": "+1234567890",
            "from": "+0987654321",
            "body": "Test message",
            "status": "sent",
            "direction": "outbound",
            "appointmentId": "apt123"
        }
        log = TwilioLogModel(**log_data)
        assert log.direction == "outbound"
        assert log.status == "sent"
    
    def test_from_field_alias(self):
        """Test that 'from' field alias works correctly"""
        log_data = {
            "to": "+1234567890",
            "from": "+0987654321",
            "body": "Test message",
            "status": "sent",
            "direction": "inbound"
        }
        log = TwilioLogModel(**log_data)
        # Access via alias
        assert log.from_ == "+0987654321"
    
    def test_invalid_direction(self):
        """Test that invalid direction raises validation error"""
        log_data = {
            "to": "+1234567890",
            "from": "+0987654321",
            "body": "Test message",
            "status": "sent",
            "direction": "invalid"
        }
        with pytest.raises(ValidationError):
            TwilioLogModel(**log_data)
