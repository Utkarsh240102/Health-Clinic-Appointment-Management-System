"""
RESTORE SCRIPT - Run this after testing to restore original constraints
"""
import shutil
import os

def restore_original_constraints():
    """Restore the original availability.py from backup"""
    
    backup_file = "app/utils/availability_BACKUP.py"
    original_file = "app/utils/availability.py"
    
    if not os.path.exists(backup_file):
        print("❌ Backup file not found!")
        return False
    
    try:
        # Copy backup to original
        shutil.copy2(backup_file, original_file)
        print("✅ Original constraints restored successfully!")
        print("\nRestored constraints:")
        print("  - Booking only on weekdays (Mon-Fri)")
        print("  - Booking only during doctor's working hours")
        print("  - 30-minute slot alignment required")
        print("  - Cannot book in the past")
        
        # Optionally delete backup
        print("\nBackup file kept at: app/utils/availability_BACKUP.py")
        print("You can delete it manually if no longer needed.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error restoring: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("RESTORING ORIGINAL BOOKING CONSTRAINTS")
    print("=" * 60)
    print("\nThis will restore:")
    print("  1. Weekend blocking (no Sat/Sun bookings)")
    print("  2. Working hours enforcement (09:00-17:00)")
    print("  3. 30-minute slot alignment")
    print("\n")
    
    confirm = input("Are you sure you want to restore? (yes/no): ")
    
    if confirm.lower() in ['yes', 'y']:
        if restore_original_constraints():
            print("\n✅ Done! Backend will auto-reload with original constraints.")
        else:
            print("\n❌ Restoration failed. Check errors above.")
    else:
        print("\n❌ Restoration cancelled.")
