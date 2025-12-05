from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    """Get current UTC time with timezone info"""
    return datetime.now(timezone.utc)


def ensure_utc(dt: datetime) -> datetime:
    """Ensure datetime is in UTC"""
    if dt.tzinfo is None:
        # Naive datetime, assume UTC
        return dt.replace(tzinfo=timezone.utc)
    else:
        # Convert to UTC
        return dt.astimezone(timezone.utc)


def parse_iso_datetime(iso_string: str) -> datetime:
    """Parse ISO datetime string to UTC datetime"""
    dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    return ensure_utc(dt)


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string"""
    return dt.isoformat()
