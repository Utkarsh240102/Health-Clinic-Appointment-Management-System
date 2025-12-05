# RESTORE ORIGINAL TWILIO TIMING SETTINGS
# Run this file after testing is complete to restore production settings

def restore_settings():
    """
    This script restores the original timing settings:
    - 3-hour reminder before appointment
    - 15-minute no-show threshold
    """
    
    import os
    from pathlib import Path
    
    base_dir = Path(__file__).parent
    
    # Files to restore
    files_to_restore = [
        {
            'file': base_dir / 'app' / 'services' / 'appointment_service.py',
            'find': '# Schedule reminder job if appointment is more than 1 minute away (TEST MODE - was 3 hours)\n        reminder_time = start - timedelta(minutes=1)',
            'replace': '# Schedule reminder job if appointment is more than 3 hours away\n        reminder_time = start - timedelta(hours=3)'
        },
        {
            'file': base_dir / 'app' / 'services' / 'scheduler_service.py',
            'find': '    - start time was more than 2 minutes ago (TEST MODE - was 15 minutes)',
            'replace': '    - start time was more than 15 minutes ago'
        },
        {
            'file': base_dir / 'app' / 'services' / 'scheduler_service.py',
            'find': 'cutoff_time = now - timedelta(minutes=2)',
            'replace': 'cutoff_time = now - timedelta(minutes=15)'
        },
        {
            'file': base_dir / 'app' / 'utils' / 'availability.py',
            'find': '    # 2. Check if aligned to slot boundaries (TEST MODE - DISABLED)\n    # if not is_slot_aligned(start, slot_duration):\n    #     return False, f"Appointment must align to {slot_duration}-minute boundaries"',
            'replace': '    # 2. Check if aligned to slot boundaries\n    if not is_slot_aligned(start, slot_duration):\n        return False, f"Appointment must align to {slot_duration}-minute boundaries"'
        },
        {
            'file': base_dir / 'app' / 'utils' / 'availability.py',
            'find': '    # 3. Check if within weekly schedule OR explicit slots (TEST MODE - DISABLED)\n    # weekly_schedule = doctor_profile.get("weeklySchedule", [])\n    # explicit_slots = doctor_profile.get("explicitSlots", [])\n    # \n    # within_weekly = is_within_weekly_schedule(start, weekly_schedule)\n    # within_explicit = is_within_explicit_slots(start, explicit_slots)\n    # \n    # if not within_weekly and not within_explicit:\n    #     return False, "Appointment time is outside doctor\'s available hours"\n    \n    return True, ""',
            'replace': '    # 3. Check if within weekly schedule OR explicit slots\n    weekly_schedule = doctor_profile.get("weeklySchedule", [])\n    explicit_slots = doctor_profile.get("explicitSlots", [])\n    \n    within_weekly = is_within_weekly_schedule(start, weekly_schedule)\n    within_explicit = is_within_explicit_slots(start, explicit_slots)\n    \n    if not within_weekly and not within_explicit:\n        return False, "Appointment time is outside doctor\'s available hours"\n    \n    return True, ""'
        }
    ]
    
    for item in files_to_restore:
        file_path = item['file']
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            new_content = content.replace(item['find'], item['replace'])
            file_path.write_text(new_content, encoding='utf-8')
            print(f"✅ Restored: {file_path.name}")
        else:
            print(f"❌ File not found: {file_path}")
    
    print("\n✅ All settings restored to production values!")
    print("Reminder: Restart the backend server for changes to take effect.")

if __name__ == "__main__":
    restore_settings()
