from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class TwilioLogModel(BaseModel):
    """Twilio SMS log model for MongoDB"""
    to: str = Field(..., description="Recipient phone number")
    from_: str = Field(..., alias="from", description="Sender phone number")
    body: str = Field(..., description="SMS message body")
    status: str = Field(..., description="Twilio delivery status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    appointmentId: Optional[str] = Field(default=None, description="Associated appointment ID")
    direction: Literal["outbound", "inbound"] = Field(..., description="Message direction")
    twilioSid: Optional[str] = Field(default=None, description="Twilio message SID")
    errorCode: Optional[str] = Field(default=None, description="Error code if failed")
    errorMessage: Optional[str] = Field(default=None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "to": "+1234567890",
                "from": "+0987654321",
                "body": "Your appointment is in 3 hours. Reply CONFIRM or CANCEL.",
                "status": "sent",
                "direction": "outbound",
                "appointmentId": "507f1f77bcf86cd799439011",
                "twilioSid": "SM1234567890abcdef"
            }
        }
        populate_by_name = True


async def create_twilio_log_indexes(db):
    """Create indexes for twilio_logs collection"""
    twilio_logs_collection = db["twilio_logs"]
    
    # Index on appointmentId for quick lookups
    await twilio_logs_collection.create_index("appointmentId")
    print("✅ Created index on twilio_logs.appointmentId")
    
    # Index on timestamp for time-based queries
    await twilio_logs_collection.create_index([("timestamp", -1)])
    print("✅ Created index on twilio_logs.timestamp")
    
    # Index on twilioSid for Twilio callback lookups
    await twilio_logs_collection.create_index("twilioSid", sparse=True)
    print("✅ Created index on twilio_logs.twilioSid")
    
    # Index on direction for filtering
    await twilio_logs_collection.create_index("direction")
    print("✅ Created index on twilio_logs.direction")
