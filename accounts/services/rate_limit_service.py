from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta

class RateLimitService:
    @staticmethod
    def check_rate_limit(key: str, max_attempts: int, window: int) -> bool:
        """Check if an action exceeds rate limits."""
        cache_key = f"ratelimit:{key}"
        now = datetime.now()
        
        # Get current attempts
        attempts = cache.get(cache_key, [])
        
        # Filter attempts within window
        valid_attempts = [
            attempt for attempt in attempts
            if attempt > now - timedelta(seconds=window)
        ]
        
        # Check if limit exceeded
        if len(valid_attempts) >= max_attempts:
            return False
            
        # Add new attempt
        valid_attempts.append(now)
        cache.set(cache_key, valid_attempts, window)
        return True