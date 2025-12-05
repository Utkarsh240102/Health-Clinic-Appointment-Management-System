"""
Initialize all database indexes on startup
"""
from app.models.user_model import create_user_indexes
from app.models.appointment_model import create_appointment_indexes
from app.models.twilio_log_model import create_twilio_log_indexes


async def initialize_indexes(db):
    """Initialize all database indexes"""
    print("\n🔧 Initializing database indexes...")
    
    await create_user_indexes(db)
    await create_appointment_indexes(db)
    await create_twilio_log_indexes(db)
    
    print("✅ All indexes created successfully\n")
