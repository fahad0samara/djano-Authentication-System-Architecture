from typing import List, Optional
from django.utils import timezone
from datetime import timedelta
from ..domain.repositories import UserRepository, LoginAttemptRepository, SecurityAuditRepository
from ..domain.models import User, LoginAttempt, SecurityAudit
from ..models import CustomUser, LoginHistory, UserActivity

class DjangoUserRepository(UserRepository):
    def get_by_id(self, user_id: int) -> Optional[User]:
        try:
            user = CustomUser.objects.get(id=user_id)
            return self._to_domain(user)
        except CustomUser.DoesNotExist:
            return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        try:
            user = CustomUser.objects.get(email=email)
            return self._to_domain(user)
        except CustomUser.DoesNotExist:
            return None
    
    def save(self, user: User) -> User:
        django_user = CustomUser.objects.create(
            username=user.username,
            email=user.email,
            is_active=user.is_active
        )
        return self._to_domain(django_user)
    
    def update(self, user: User) -> User:
        django_user = CustomUser.objects.get(id=user.id)
        django_user.username = user.username
        django_user.email = user.email
        django_user.is_active = user.is_active
        django_user.save()
        return self._to_domain(django_user)
    
    def _to_domain(self, django_user: CustomUser) -> User:
        return User(
            id=django_user.id,
            username=django_user.username,
            email=django_user.email,
            is_active=django_user.is_active,
            date_joined=django_user.date_joined,
            last_login=django_user.last_login,
            two_factor_enabled=django_user.two_factor_enabled
        )

class DjangoLoginAttemptRepository(LoginAttemptRepository):
    def create(self, attempt: LoginAttempt) -> LoginAttempt:
        history = LoginHistory.objects.create(
            user_id=attempt.user_id,
            timestamp=attempt.timestamp,
            ip_address=attempt.ip_address,
            user_agent=attempt.user_agent,
            status=attempt.status
        )
        return self._to_domain(history)
    
    def get_recent_attempts(self, user_id: int, hours: int = 24) -> List[LoginAttempt]:
        attempts = LoginHistory.objects.filter(
            user_id=user_id,
            timestamp__gte=timezone.now() - timedelta(hours=hours)
        )
        return [self._to_domain(attempt) for attempt in attempts]
    
    def get_failed_attempts(self, user_id: int, minutes: int = 30) -> List[LoginAttempt]:
        attempts = LoginHistory.objects.filter(
            user_id=user_id,
            status='failed',
            timestamp__gte=timezone.now() - timedelta(minutes=minutes)
        )
        return [self._to_domain(attempt) for attempt in attempts]
    
    def _to_domain(self, history: LoginHistory) -> LoginAttempt:
        return LoginAttempt(
            id=history.id,
            user_id=history.user_id,
            timestamp=history.timestamp,
            ip_address=history.ip_address,
            user_agent=history.user_agent,
            status=history.status
        )

class DjangoSecurityAuditRepository(SecurityAuditRepository):
    def log(self, audit: SecurityAudit) -> SecurityAudit:
        activity = UserActivity.objects.create(
            user_id=audit.user_id,
            action=audit.action,
            timestamp=audit.timestamp,
            ip_address=audit.ip_address,
            metadata=audit.metadata
        )
        return self._to_domain(activity)
    
    def get_user_activity(self, user_id: int, days: int = 30) -> List[SecurityAudit]:
        activities = UserActivity.objects.filter(
            user_id=user_id,
            timestamp__gte=timezone.now() - timedelta(days=days)
        )
        return [self._to_domain(activity) for activity in activities]
    
    def _to_domain(self, activity: UserActivity) -> SecurityAudit:
        return SecurityAudit(
            id=activity.id,
            user_id=activity.user_id,
            action=activity.action,
            timestamp=activity.timestamp,
            ip_address=activity.ip_address,
            metadata=activity.metadata
        )