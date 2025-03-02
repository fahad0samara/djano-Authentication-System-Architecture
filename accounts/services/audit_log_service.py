from typing import Dict, Any
from django.utils import timezone
from ..models import UserActivity
from ..utils.ip import get_client_ip, get_country_code

class AuditLogService:
    @staticmethod
    def log_security_event(
        user_id: int,
        event_type: str,
        request: Any,
        metadata: Dict = None
    ) -> None:
        """Log security-related events."""
        ip = get_client_ip(request)
        
        UserActivity.objects.create(
            user_id=user_id,
            action=f"security_{event_type}",
            metadata={
                **(metadata or {}),
                "ip": ip,
                "country": get_country_code(ip),
                "timestamp": timezone.now().isoformat()
            }
        )