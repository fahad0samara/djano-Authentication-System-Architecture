from typing import List
from django.utils import timezone
from ...application.ports import SecurityAuditRepository
from ...application.dtos import SecurityAuditDTO
from ..models import UserActivity

class DjangoSecurityAuditRepository(SecurityAuditRepository):
    def save_audit(self, audit: SecurityAuditDTO) -> None:
        UserActivity.objects.create(
            user_id=audit.user_id,
            action=audit.action,
            timestamp=audit.timestamp,
            ip_address=audit.ip_address,
            metadata=audit.metadata
        )
    
    def get_user_audits(self, user_id: int, limit: int = 100) -> List[SecurityAuditDTO]:
        audits = UserActivity.objects.filter(
            user_id=user_id
        ).order_by('-timestamp')[:limit]
        
        return [self._to_dto(audit) for audit in audits]
    
    def _to_dto(self, audit: UserActivity) -> SecurityAuditDTO:
        return SecurityAuditDTO(
            timestamp=audit.timestamp,
            action=audit.action,
            ip_address=audit.ip_address,
            metadata=audit.metadata
        )