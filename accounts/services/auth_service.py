from typing import Optional, Tuple
from django.contrib.auth import get_user_model
from django.http import HttpRequest

from ..models import LoginHistory, FailedLoginAttempt

User = get_user_model()

class AuthenticationService:
    @staticmethod
    def record_login_attempt(request: HttpRequest, username: str, success: bool) -> None:
        """Record a login attempt in the history."""
        if success and request.user.is_authenticated:
            LoginHistory.objects.create(
                user=request.user,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                status='success'
            )
        else:
            LoginHistory.objects.create(
                user=User.objects.filter(username=username).first(),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                status='failed'
            )
    
    @staticmethod
    def check_login_attempts(username: str, ip_address: str) -> Tuple[bool, Optional[str]]:
        """Check if login should be allowed based on previous attempts."""
        attempt = FailedLoginAttempt.objects.filter(
            username=username,
            ip_address=ip_address
        ).first()
        
        if attempt and attempt.attempt_count >= 5:
            return False, "Too many failed attempts. Please try again later."
        return True, None