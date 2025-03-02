from typing import Dict, Optional
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from ..models import CustomUser
from .device_fingerprint_service import DeviceFingerprintService
import logging

logger = logging.getLogger(__name__)

class SessionSecurityService:
    # Constants for configuration
    CACHE_PREFIX = "session_security:"
    MAX_CONCURRENT_SESSIONS = 5
    SESSION_IDLE_TIMEOUT = 30  # minutes
    SUSPICIOUS_ACTIVITY_THRESHOLD = 100  # requests per 5 minutes
    
    @staticmethod
    def validate_session(
        session_key: str,
        user_id: int,
        request_data: Dict
    ) -> Dict:
        """
        Validate session integrity and security.
        
        Args:
            session_key: The session key to validate
            user_id: The user ID associated with the session
            request_data: Dictionary containing request information
            
        Returns:
            Dict containing validation results
        """
        try:
            # Check session existence and expiry
            session = Session.objects.filter(session_key=session_key).first()
            if not session:
                return {"valid": False, "reason": "session_not_found"}
            
            # Check session age
            session_age = timezone.now() - (session.expire_date - timedelta(weeks=2))
            if session_age > timedelta(minutes=SessionSecurityService.SESSION_IDLE_TIMEOUT):
                return {"valid": False, "reason": "session_expired"}
            
            # Verify device fingerprint
            device_fingerprint = DeviceFingerprintService.generate_fingerprint(request_data)
            if not SessionSecurityService._verify_device_fingerprint(session_key, device_fingerprint):
                return {"valid": False, "reason": "invalid_device"}
            
            # Check for suspicious activity
            if SessionSecurityService._detect_suspicious_activity(session_key):
                return {"valid": False, "reason": "suspicious_activity"}
            
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"Error validating session: {str(e)}")
            return {"valid": False, "reason": "validation_error"}
    
    @staticmethod
    def enforce_session_limits(user_id: int) -> None:
        """
        Enforce maximum number of concurrent sessions.
        
        Args:
            user_id: The user ID to check
        """
        try:
            sessions = Session.objects.filter(
                expire_date__gt=timezone.now()
            )
            
            user_sessions = []
            for session in sessions:
                data = session.get_decoded()
                if str(data.get('_auth_user_id')) == str(user_id):
                    user_sessions.append(session)
            
            # If too many sessions, remove oldest
            if len(user_sessions) > SessionSecurityService.MAX_CONCURRENT_SESSIONS:
                user_sessions.sort(key=lambda s: s.expire_date)
                for session in user_sessions[:(len(user_sessions) - SessionSecurityService.MAX_CONCURRENT_SESSIONS)]:
                    session.delete()
                    
        except Exception as e:
            logger.error(f"Error enforcing session limits: {str(e)}")
    
    @staticmethod
    def _verify_device_fingerprint(session_key: str, fingerprint: str) -> bool:
        """Verify device fingerprint matches session."""
        try:
            cache_key = f"{SessionSecurityService.CACHE_PREFIX}device:{session_key}"
            stored_fingerprint = cache.get(cache_key)
            
            if not stored_fingerprint:
                # First time seeing this session, store the fingerprint
                cache.set(cache_key, fingerprint, timeout=86400)  # 24 hours
                return True
            
            return stored_fingerprint == fingerprint
            
        except Exception as e:
            logger.error(f"Error verifying device fingerprint: {str(e)}")
            return False
    
    @staticmethod
    def _detect_suspicious_activity(session_key: str) -> bool:
        """Detect suspicious activity patterns."""
        try:
            cache_key = f"{SessionSecurityService.CACHE_PREFIX}activity:{session_key}"
            activity_count = cache.get(cache_key, 0)
            
            if activity_count > SessionSecurityService.SUSPICIOUS_ACTIVITY_THRESHOLD:
                return True
            
            # Increment activity counter
            cache.set(cache_key, activity_count + 1, timeout=300)  # 5 minutes
            return False
            
        except Exception as e:
            logger.error(f"Error detecting suspicious activity: {str(e)}")
            return True  # Fail safe