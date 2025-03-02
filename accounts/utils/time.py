from datetime import datetime, timezone
from typing import Optional

def utc_now() -> datetime:
    """Get current UTC timestamp."""
    return datetime.now(timezone.utc)

def parse_timestamp(timestamp: str) -> Optional[datetime]:
    """Parse ISO format timestamp."""
    try:
        return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None