from abc import ABC, abstractmethod
from typing import List, Optional
from .models import User, LoginAttempt, SecurityAudit

class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass
        
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass
        
    @abstractmethod
    def save(self, user: User) -> User:
        pass
        
    @abstractmethod
    def update(self, user: User) -> User:
        pass

class LoginAttemptRepository(ABC):
    @abstractmethod
    def create(self, attempt: LoginAttempt) -> LoginAttempt:
        pass
        
    @abstractmethod
    def get_recent_attempts(self, user_id: int, hours: int = 24) -> List[LoginAttempt]:
        pass
        
    @abstractmethod
    def get_failed_attempts(self, user_id: int, minutes: int = 30) -> List[LoginAttempt]:
        pass

class SecurityAuditRepository(ABC):
    @abstractmethod
    def log(self, audit: SecurityAudit) -> SecurityAudit:
        pass
        
    @abstractmethod
    def get_user_activity(self, user_id: int, days: int = 30) -> List[SecurityAudit]:
        pass