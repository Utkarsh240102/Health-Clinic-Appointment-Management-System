from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/now")
async def get_server_time():
    """
    Get current server time in UTC
    
    - Used by clients to sync their clocks
    - Returns ISO formatted UTC timestamp
    """
    return {
        "server_utc": datetime.utcnow().isoformat() + "Z"
    }
