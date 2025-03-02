from typing import Optional, Dict
from datetime import datetime
from .repositories import UserRepository, LoginAttemptRepository, SecurityAuditRepository
from .models import User, LoginAttempt, SecurityAudit
from ..services.security_service import SecurityService
from ..services.notification_service import NotificationService

class AuthenticationUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        login_repo: LoginAttemptRepository,
        security_service: SecurityService
    ):
        self.user_repo = user_repo
        self.login_repo = login_repo
        self.security_service = security_service
    
    def authenticate(self, email: str, password: str, ip_address: str, user_agent: str) -> Dict:
        user = self.user_repo.get_by_email(email)
        if not user:
            self._record_failed_attempt(None, ip_address, user_agent)
            return {"success": False, "message": "Invalid credentials"}
            
        if not self.security_service.verify_password(password, user.password):
            self._record_failed_attempt(user.id, ip_address, user_agent)
            return {"success": False, "message": "Invalid credentials"}
            
        self._record_successful_attempt(user.id, ip_address, user_agent)
        return {"success": True, "user": user}
    
    def _record_failed_attempt(self, user_id: Optional[int], ip_address: str, user_agent: str):
        attempt = LoginAttempt(
            id=None,
            user_id=user_id,
            timestamp=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent,
            status="failed"
        )
        self.login_repo.create(attempt)

class SecurityAuditUseCase:
    def __init__(
        self,
        audit_repo: SecurityAuditRepository,
        notification_service: NotificationService
    ):
        self.audit_repo = audit_repo
        self.notification_service = notification_service
    
    def log_security_event(
        self,
        user_id: int,
        action: str,
        ip_address: str,
        metadata: dict = None
    ) -> None:
        audit = SecurityAudit(
            id=None,
            user_id=user_id,
            action=action,
            timestamp=datetime.now(),
            ip_address=ip_address,
            metadata=metadata or {}
        )
        self.audit_repo.log(audit)
        
        if action in ["password_changed", "2fa_disabled", "suspicious_login"]:
            self.notification_service.send_security_alert(
                user_id,
                action,
                metadata
            )