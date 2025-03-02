from typing import Dict, Optional
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.core.exceptions import ValidationError
from ..models import CustomUser
from .notification_service import NotificationService
from ..utils.validators import validate_username
import logging

logger = logging.getLogger(__name__)

class AccountSecurityService:
    # Constants for configuration
    CACHE_PREFIX = "account_security:"
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_MINUTES = 30
    PASSWORD_MAX_AGE_DAYS = 90
    MAX_STORED_ATTEMPTS = 100
    
    @staticmethod
    def check_account_lockout(username: str) -> Dict:
        """
        Check if account is locked due to failed attempts.
        
        Args:
            username: The username to check
            
        Returns:
            Dict containing lockout status
            
        Raises:
            ValidationError: If username is invalid
        """
        try:
            validate_username(username)
            
            cache_key = f"{AccountSecurityService.CACHE_PREFIX}lockout:{username}"
            attempts = cache.get(cache_key, [])
            current_time = timezone.now()
            
            # Clean old attempts
            attempts = [
                attempt for attempt in attempts
                if attempt > current_time - timedelta(minutes=AccountSecurityService.LOCKOUT_MINUTES)
            ]
            
            is_locked = len(attempts) >= AccountSecurityService.MAX_LOGIN_ATTEMPTS
            remaining_attempts = max(0, AccountSecurityService.MAX_LOGIN_ATTEMPTS - len(attempts))
            
            return {
                "is_locked": is_locked,
                "remaining_attempts": remaining_attempts,
                "lockout_expires": current_time + timedelta(minutes=AccountSecurityService.LOCKOUT_MINUTES) if is_locked else None
            }
            
        except ValidationError as e:
            raise
        except Exception as e:
            logger.error(f"Error checking account lockout: {str(e)}")
            # Default to locked on error for safety
            return {
                "is_locked": True,
                "remaining_attempts": 0,
                "lockout_expires": timezone.now() + timedelta(minutes=AccountSecurityService.LOCKOUT_MINUTES)
            }
    
    @staticmethod
    def record_login_attempt(username: str, success: bool) -> None:
        """
        Record a login attempt for lockout tracking.
        
        Args:
            username: The username to record
            success: Whether the login attempt was successful
            
        Raises:
            ValidationError: If username is invalid
        """
        try:
            validate_username(username)
            
            if success:
                # Clear failed attempts on successful login
                cache.delete(f"{AccountSecurityService.CACHE_PREFIX}lockout:{username}")
                return
            
            cache_key = f"{AccountSecurityService.CACHE_PREFIX}lockout:{username}"
            attempts = cache.get(cache_key, [])
            current_time = timezone.now()
            
            # Clean old attempts and enforce maximum
            attempts = [
                attempt for attempt in attempts
                if attempt > current_time - timedelta(minutes=AccountSecurityService.LOCKOUT_MINUTES)
            ][-AccountSecurityService.MAX_STORED_ATTEMPTS:]
            
            attempts.append(current_time)
            cache.set(cache_key, attempts, timeout=AccountSecurityService.LOCKOUT_MINUTES * 60)
            
            # Notify user of failed attempts at specific thresholds
            if len(attempts) in [3, AccountSecurityService.MAX_LOGIN_ATTEMPTS]:
                user = CustomUser.objects.filter(username=username).first()
                if user:
                    NotificationService.send_security_alert(
                        user,
                        "failed_login_attempts",
                        {
                            "attempt_count": len(attempts),
                            "lockout_threshold": AccountSecurityService.MAX_LOGIN_ATTEMPTS,
                            "remaining_attempts": AccountSecurityService.MAX_LOGIN_ATTEMPTS - len(attempts)
                        }
                    )
                    
        except ValidationError as e:
            raise
        except Exception as e:
            logger.error(f"Error recording login attempt: {str(e)}")
    
    @staticmethod
    def enforce_password_expiry(user: CustomUser) -> Dict:
        """
        Check if password has expired and needs reset.
        
        Args:
            user: The user to check
            
        Returns:
            Dict containing password expiry status
        """
        try:
            if not user.password_changed_at:
                return {
                    "password_expired": True,
                    "days_until_expiry": 0,
                    "last_changed": None
                }
            
            max_age = timedelta(days=AccountSecurityService.PASSWORD_MAX_AGE_DAYS)
            password_age = timezone.now() - user.password_changed_at
            days_until_expiry = max(0, (max_age - password_age).days)
            
            # Notify user when password is close to expiring
            if 0 < days_until_expiry <= 7:
                NotificationService.send_security_alert(
                    user,
                    "password_expiring",
                    {"days_remaining": days_until_expiry}
                )
            
            return {
                "password_expired": password_age > max_age,
                "days_until_expiry": days_until_expiry,
                "last_changed": user.password_changed_at
            }
            
        except Exception as e:
            logger.error(f"Error checking password expiry: {str(e)}")
            # Default to expired on error for safety
            return {
                "password_expired": True,
                "days_until_expiry": 0,
                "last_changed": None
            }