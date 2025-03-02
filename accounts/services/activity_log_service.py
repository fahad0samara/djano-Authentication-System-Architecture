from django.utils import timezone
from ..models import UserActivity

class ActivityLogService:
    @staticmethod
    def log_activity(user_id: int, action: str, metadata: dict = None) -> None:
        """Log user activities for audit purposes."""
        UserActivity.objects.create(
            user_id=user_id,
            action=action,
            metadata=metadata or {},
            timestamp=timezone.now()
        )