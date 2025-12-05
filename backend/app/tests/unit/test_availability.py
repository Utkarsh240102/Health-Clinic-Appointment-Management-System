import pytest
from app.utils.availability import (
    parse_time,
    is_slot_aligned,
    is_within_weekly_schedule,
    validate_appointment_slot,
    generate_slots_for_day
)
from datetime import datetime, timedelta


class TestAvailabilityUtils:
    """Test availability utility functions"""
    
    def test_parse_time(self):
        """Test time parsing"""
        assert parse_time("09:00") == (9, 0)
        assert parse_time("17:30") == (17, 30)
        assert parse_time("00:00") == (0, 0)
        assert parse_time("23:59") == (23, 59)
        
        # Invalid formats
        with pytest.raises(ValueError):
            parse_time("25:00")
        with pytest.raises(ValueError):
            parse_time("12:60")
    
    def test_is_slot_aligned(self):
        """Test slot alignment check"""
        # Aligned to 30-minute boundaries
        assert is_slot_aligned(datetime(2025, 11, 20, 9, 0), 30) is True
        assert is_slot_aligned(datetime(2025, 11, 20, 9, 30), 30) is True
        assert is_slot_aligned(datetime(2025, 11, 20, 10, 0), 30) is True
        
        # Not aligned
        assert is_slot_aligned(datetime(2025, 11, 20, 9, 15), 30) is False
        assert is_slot_aligned(datetime(2025, 11, 20, 9, 45), 30) is False
    
    def test_is_within_weekly_schedule(self):
        """Test weekly schedule validation"""
        # Monday 09:00-17:00, Wednesday 09:00-17:00
        weekly_schedule = [
            {"weekday": 0, "start": "09:00", "end": "17:00"},
            {"weekday": 2, "start": "09:00", "end": "17:00"}
        ]
        
        # Monday 10:00 - should be within schedule
        monday_10am = datetime(2025, 11, 17, 10, 0)  # Monday
        assert is_within_weekly_schedule(monday_10am, weekly_schedule) is True
        
        # Tuesday 10:00 - not in schedule
        tuesday_10am = datetime(2025, 11, 18, 10, 0)  # Tuesday
        assert is_within_weekly_schedule(tuesday_10am, weekly_schedule) is False
        
        # Monday 18:00 - after hours
        monday_6pm = datetime(2025, 11, 17, 18, 0)
        assert is_within_weekly_schedule(monday_6pm, weekly_schedule) is False
    
    def test_validate_appointment_slot(self):
        """Test appointment slot validation"""
        doctor_profile = {
            "slotDurationMin": 30,
            "weeklySchedule": [
                {"weekday": 0, "start": "09:00", "end": "17:00"}
            ]
        }
        
        now = datetime(2025, 11, 17, 8, 0)  # Monday 8am
        
        # Valid appointment: Monday 10:00
        future_slot = datetime(2025, 11, 17, 10, 0)
        is_valid, msg = validate_appointment_slot(future_slot, doctor_profile, now)
        assert is_valid is True
        
        # Past appointment
        past_slot = datetime(2025, 11, 17, 7, 0)
        is_valid, msg = validate_appointment_slot(past_slot, doctor_profile, now)
        assert is_valid is False
        assert "past" in msg.lower()
        
        # Not aligned
        unaligned_slot = datetime(2025, 11, 17, 10, 15)
        is_valid, msg = validate_appointment_slot(unaligned_slot, doctor_profile, now)
        assert is_valid is False
        assert "align" in msg.lower()
        
        # Outside schedule (Tuesday)
        outside_schedule = datetime(2025, 11, 18, 10, 0)
        is_valid, msg = validate_appointment_slot(outside_schedule, doctor_profile, now)
        assert is_valid is False
        assert "outside" in msg.lower()
    
    def test_generate_slots_for_day(self):
        """Test slot generation"""
        doctor_profile = {
            "slotDurationMin": 30,
            "weeklySchedule": [
                {"weekday": 0, "start": "09:00", "end": "11:00"}  # 2 hours = 4 slots
            ]
        }
        
        # Monday
        monday = datetime(2025, 11, 17, 0, 0)
        slots = generate_slots_for_day(monday, doctor_profile)
        
        assert len(slots) == 4
        assert slots[0]["start"] == datetime(2025, 11, 17, 9, 0)
        assert slots[0]["end"] == datetime(2025, 11, 17, 9, 30)
        assert slots[3]["start"] == datetime(2025, 11, 17, 10, 30)
        assert slots[3]["end"] == datetime(2025, 11, 17, 11, 0)
        
        # Tuesday (no schedule)
        tuesday = datetime(2025, 11, 18, 0, 0)
        slots_tuesday = generate_slots_for_day(tuesday, doctor_profile)
        assert len(slots_tuesday) == 0
