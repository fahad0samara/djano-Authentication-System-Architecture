from abc import ABC, abstractmethod
from typing import Any
from datetime import datetime, timedelta

class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, candidate: Any) -> bool:
        pass

class PasswordStrengthSpecification(Specification):
    def is_satisfied_by(self, password: str) -> bool:
        """Check if password meets strength requirements."""
        if len(password) < 10:
            return False
            
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        return all([has_upper, has_lower, has_digit, has_special])

class LoginAttemptSpecification(Specification):
    def __init__(self, max_attempts: int = 5, window_minutes: int = 30):
        self.max_attempts = max_attempts
        self.window_minutes = window_minutes
    
    def is_satisfied_by(self, attempts: list) -> bool:
        """Check if login attempts are within acceptable limits."""
        recent_attempts = [
            attempt for attempt in attempts
            if attempt.timestamp > datetime.now() - timedelta(minutes=self.window_minutes)
        ]
        return len(recent_attempts) < self.max_attempts

class DeviceTrustSpecification(Specification):
    def is_satisfied_by(self, device: Any) -> bool:
        """Check if device meets trust requirements."""
        if not device:
            return False
            
        return (
            device.is_trusted and
            device.last_used > datetime.now() - timedelta(days=30)
        )