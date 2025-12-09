from datetime import datetime, timedelta
from typing import List, Tuple
import re


def parse_time(time_str: str) -> Tuple[int, int]:
    """Parse time string 'HH:MM' into (hour, minute) tuple"""
    match = re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', time_str)
    if not match:
        raise ValueError(f"Invalid time format: {time_str}")
    return int(match.group(1)), int(match.group(2))


def is_slot_aligned(dt: datetime, slot_duration_min: int = 30) -> bool:
    """Check if datetime aligns to slot boundaries (e.g., 09:00, 09:30, 10:00)"""
    minutes_from_hour = dt.minute
    return minutes_from_hour % slot_duration_min == 0


def is_within_weekly_schedule(dt: datetime, weekly_schedule: List[dict]) -> bool:
    """Check if datetime falls within doctor's weekly schedule"""
    if not weekly_schedule:
        return False
    
    # Get weekday (0=Monday, 6=Sunday)
    weekday = dt.weekday()
    
    # Check if this weekday has a schedule
    for schedule in weekly_schedule:
        if schedule["weekday"] == weekday:
            # Parse schedule times
            start_hour, start_min = parse_time(schedule["start"])
            end_hour, end_min = parse_time(schedule["end"])
            
            # Create datetime objects for comparison (same date as dt)
            schedule_start = dt.replace(hour=start_hour, minute=start_min, second=0, microsecond=0)
            schedule_end = dt.replace(hour=end_hour, minute=end_min, second=0, microsecond=0)
            
            # Check if appointment time is within schedule
            if schedule_start <= dt < schedule_end:
                return True
    
    return False


def is_within_explicit_slots(dt: datetime, explicit_slots: List[datetime]) -> bool:
    """Check if datetime matches any explicit slot"""
    if not explicit_slots:
        return False
    
    # Check if dt matches any explicit slot (exact match)
    for slot in explicit_slots:
        if abs((slot - dt).total_seconds()) < 60:  # Within 1 minute
            return True
    
    return False


def validate_appointment_slot(
    start: datetime,
    doctor_profile: dict,
    now: datetime = None
) -> Tuple[bool, str]:
    """
    Validate appointment slot against doctor's schedule
    
    Returns (is_valid, error_message)
    """
    if now is None:
        now = datetime.utcnow()
    
    slot_duration = doctor_profile.get("slotDurationMin", 30)
    
    # 1. Check if in the past
    if start <= now:
        return False, "Cannot book appointments in the past"
    
    # 2. Check if aligned to slot boundaries
    if not is_slot_aligned(start, slot_duration):
        return False, f"Appointment must align to {slot_duration}-minute boundaries"
    
    # 3. Check if within weekly schedule OR explicit slots
    weekly_schedule = doctor_profile.get("weeklySchedule", [])
    explicit_slots = doctor_profile.get("explicitSlots", [])
    
    within_weekly = is_within_weekly_schedule(start, weekly_schedule)
    within_explicit = is_within_explicit_slots(start, explicit_slots)
    
    if not within_weekly and not within_explicit:
        return False, "Appointment time is outside doctor's available hours"
    
    return True, ""


def generate_slots_for_day(
    date: datetime,
    doctor_profile: dict
) -> List[dict]:
    """
    Generate all possible slots for a given date based on doctor's schedule
    
    Returns list of slot dicts with start/end times
    """
    slots = []
    slot_duration = doctor_profile.get("slotDurationMin", 30)
    weekly_schedule = doctor_profile.get("weeklySchedule", [])
    
    # Get weekday
    weekday = date.weekday()
    
    # Find schedules for this weekday
    for schedule in weekly_schedule:
        if schedule["weekday"] == weekday:
            start_hour, start_min = parse_time(schedule["start"])
            end_hour, end_min = parse_time(schedule["end"])
            
            # Create start and end times
            current = date.replace(hour=start_hour, minute=start_min, second=0, microsecond=0)
            end = date.replace(hour=end_hour, minute=end_min, second=0, microsecond=0)
            
            # Generate slots
            while current < end:
                slot_end = current + timedelta(minutes=slot_duration)
                if slot_end <= end:
                    slots.append({
                        "start": current,
                        "end": slot_end
                    })
                current = slot_end
    
    return slots


def filter_past_slots(slots: List[dict], now: datetime = None) -> List[dict]:
    """Filter out slots that are in the past"""
    if now is None:
        now = datetime.utcnow()
    
    return [slot for slot in slots if slot["start"] > now]
