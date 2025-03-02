from datetime import datetime
from typing import Optional, List
from .models import User, LoginAttempt
from .value_objects import DeviceFingerprint, SecurityToken
from .events import SecurityAlert
from .exceptions import SecurityError

class SecurityPolicyService:
    def __init__(self, max_attempts: int = 5, lockout_minutes: int = 30):
        self.max_attempts = max_attempts
        self.lockout_minutes = lockout_minutes
    
    def validate_login_attempt(
        self,
        user: User,
        attempts: List[LoginAttempt],
        device: DeviceFingerprint
    ) -> bool:
        recent_failures = [a for a in attempts if not a.success]
        
        if len(recent_failures) >= self.max_attempts:
            raise SecurityError("Account temporarily locked")
            
        if user.two_factor_enabled and not self._is_trusted_device(user, device):
            return False
            
        return True
    
    def _is_trusted_device(self, user: User, device: DeviceFingerprint) -> bool:
        # Implementation would check against user's trusted devices
        return False

class TokenService:
    def create_token(self, user_id: int, purpose: str, expires_in_minutes: int = 60) -> SecurityToken:
        return SecurityToken(
            value=self._generate_secure_token(),
            purpose=purpose,
            expires_at=datetime.now() + timedelta(minutes=expires_in_minutes)
        )
    
    def validate_token(self, token: SecurityToken) -> bool:
        if token.is_used:
            raise SecurityError("Token already used")
            
        if token.expires_at < datetime.now():
            raise SecurityError("Token expired")
            
        return True
    
    def _generate_secure_token(self) -> str:
        return secrets.token_urlsafe(32)