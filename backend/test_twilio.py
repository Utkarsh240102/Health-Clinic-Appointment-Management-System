"""
Test Twilio SMS manually to see the actual error
"""
import asyncio
from twilio.rest import Client
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings

async def test_twilio():
    print("=" * 60)
    print("TESTING TWILIO SMS")
    print("=" * 60)
    
    print(f"\nTwilio Configuration:")
    print(f"Account SID: {settings.TWILIO_ACCOUNT_SID[:10]}..." if settings.TWILIO_ACCOUNT_SID else "MISSING")
    print(f"Auth Token: {'*' * 20} (hidden)")
    print(f"From Number: {settings.TWILIO_FROM_PATIENT}")
    
    try:
        # Initialize client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        print(f"\n✅ Twilio client initialized")
        
        # Test sending SMS
        to_number = "+917017982662"
        message_body = "Test message from Health Clinic - Testing SMS functionality"
        
        print(f"\nAttempting to send SMS...")
        print(f"To: {to_number}")
        print(f"From: {settings.TWILIO_FROM_PATIENT}")
        print(f"Body: {message_body}")
        
        message = client.messages.create(
            to=to_number,
            from_=settings.TWILIO_FROM_PATIENT,
            body=message_body
        )
        
        print(f"\n✅ SMS SENT SUCCESSFULLY!")
        print(f"Message SID: {message.sid}")
        print(f"Status: {message.status}")
        print(f"Price: {message.price}")
        print(f"Direction: {message.direction}")
        
    except Exception as e:
        print(f"\n❌ FAILED TO SEND SMS")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print(f"\nFull Error:")
        import traceback
        traceback.print_exc()
        
        # Common error interpretations
        error_str = str(e).lower()
        print(f"\n💡 Likely Cause:")
        if "authenticate" in error_str or "20003" in error_str:
            print("   - Invalid Twilio credentials (Account SID or Auth Token)")
            print("   - Check your .env file")
        elif "21608" in error_str:
            print("   - Phone number not verified (Trial account)")
            print("   - Verify +917017982662 in Twilio Console")
        elif "21211" in error_str:
            print("   - Invalid 'To' phone number format")
        elif "21606" in error_str:
            print("   - 'From' number not valid or not owned by your account")
        else:
            print("   - Unknown error, check Twilio dashboard")

if __name__ == "__main__":
    asyncio.run(test_twilio())
