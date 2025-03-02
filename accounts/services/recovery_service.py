from typing import Optional
from django.utils import timezone
from ..models import CustomUser
from .token_service import TokenService
from .notification_service import NotificationService

class RecoveryService:
    @staticmethod
    def initiate_recovery(email: str) -> Optional[str]:
        """Initiate account recovery process."""
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            return None
            
        token = TokenService.generate_token(user.id, "recovery")
        NotificationService.send_security_alert(
            user, 
            "account_recovery",
            {"recovery_token": token}
        )
        return token
    
    @staticmethod
    def verify_recovery(token: str) -> Optional[CustomUser]:
        """Verify recovery token."""
        user_id = TokenService.verify_token(token, "recovery", max_age=3600)
        if not user_id:
            return None
            
        return CustomUser.objects.filter(id=user_id).first()