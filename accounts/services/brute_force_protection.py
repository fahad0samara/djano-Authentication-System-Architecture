from typing import Dict, Optional, List
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.core.exceptions import ValidationError
from ..utils.ip import validate_ip_address
from ..utils.validators import validate_username
import logging

logger = logging.getLogger(__name__)

class BruteForceProtection:
    # Constants for configuration
    CACHE_PREFIX = "brute_force:"
    IP_MAX_ATTEMPTS = 20
    IP_WINDOW_MINUTES = 15
    USERNAME_MAX_ATTEMPTS = 50
    USERNAME_WINDOW_MINUTES = 60
    MAX_STORED_ATTEMPTS = 100  # Limit stored attempts to prevent memory issues
    
    @staticmethod
    def check_ip_rate_limit(ip_address: str) -> Dict:
        """
        Check if IP has exceeded rate limits.
        
        Args:
            ip_address: The IP address to check
            
        Returns:
            Dict containing rate limit status
            
        Raises:
            ValidationError: If IP address is invalid
        """
        try:
            validate_ip_address(ip_address)
            
            cache_key = f"{BruteForceProtection.CACHE_PREFIX}ip:{ip_address}"
            return BruteForceProtection._check_rate_limit(
                cache_key,
                BruteForceProtection.IP_MAX_ATTEMPTS,
                BruteForceProtection.IP_WINDOW_MINUTES
            )
            
        except ValidationError as e:
            raise
        except Exception as e:
            logger.error(f"Error checking IP rate limit: {str(e)}")
            # Default to blocked on error for safety
            return {
                "is_blocked": True,
                "remaining_attempts": 0,
                "block_expires": timezone.now() + timedelta(minutes=BruteForceProtection.IP_WINDOW_MINUTES)
            }
    
    @staticmethod
    def record_ip_attempt(ip_address: str) -> None:
        """
        Record an attempt from an IP address.
        
        Args:
            ip_address: The IP address to record
            
        Raises:
            ValidationError: If IP address is invalid
        """
        try:
            validate_ip_address(ip_address)
            
            cache_key = f"{BruteForceProtection.CACHE_PREFIX}ip:{ip_address}"
            BruteForceProtection._record_attempt(
                cache_key,
                BruteForceProtection.IP_WINDOW_MINUTES
            )
            
        except ValidationError as e:
            raise
        except Exception as e:
            logger.error(f"Error recording IP attempt: {str(e)}")
    
    @staticmethod
    def check_username_rate_limit(username: str) -> Dict:
        """
        Check if too many attempts for a username across IPs.
        
        Args:
            username: The username to check
            
        Returns:
            Dict containing rate limit status
            
        Raises:
            ValidationError: If username is invalid
        """
        try:
            validate_username(username)
            
            cache_key = f"{BruteForceProtection.CACHE_PREFIX}user:{username}"
            return BruteForceProtection._check_rate_limit(
                cache_key,
                BruteForceProtection.USERNAME_MAX_ATTEMPTS,
                BruteForceProtection.USERNAME_WINDOW_MINUTES
            )
            
        except ValidationError as e:
            raise
        except Exception as e:
            logger.error(f"Error checking username rate limit: {str(e)}")
            return {
                "is_blocked": True,
                "remaining_attempts": 0,
                "block_expires": timezone.now() + timedelta(minutes=BruteForceProtection.USERNAME_WINDOW_MINUTES)
            }
    
    @staticmethod
    def _check_rate_limit(cache_key: str, max_attempts: int, window_minutes: int) -> Dict:
        """Check rate limit for a given cache key."""
        try:
            attempts = cache.get(cache_key, [])
            current_time = timezone.now()
            
            # Clean old attempts
            attempts = [
                attempt for attempt in attempts
                if attempt > current_time - timedelta(minutes=window_minutes)
            ]
            
            is_blocked = len(attempts) >= max_attempts
            remaining_attempts = max(0, max_attempts - len(attempts))
            
            return {
                "is_blocked": is_blocked,
                "remaining_attempts": remaining_attempts,
                "block_expires": current_time + timedelta(minutes=window_minutes) if is_blocked else None
            }
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            return {
                "is_blocked": True,
                "remaining_attempts": 0,
                "block_expires": timezone.now() + timedelta(minutes=window_minutes)
            }
    
    @staticmethod
    def _record_attempt(cache_key: str, window_minutes: int) -> None:
        """Record an attempt in the cache."""
        try:
            attempts = cache.get(cache_key, [])
            current_time = timezone.now()
            
            # Clean old attempts and enforce maximum
            attempts = [
                attempt for attempt in attempts
                if attempt > current_time - timedelta(minutes=window_minutes)
            ][-BruteForceProtection.MAX_STORED_ATTEMPTS:]
            
            attempts.append(current_time)
            cache.set(cache_key, attempts, timeout=window_minutes * 60)
            
        except Exception as e:
            logger.error(f"Error recording attempt: {str(e)}")
            # Continue without recording on error