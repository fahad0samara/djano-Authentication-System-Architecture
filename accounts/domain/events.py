from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict

@dataclass
class DomainEvent:
    timestamp: datetime
    user_id: Optional[int]

@dataclass
class UserCreated(DomainEvent):
    username: str
    email: str

@dataclass
class LoginAttempted(DomainEvent):
    success: bool
    ip_address: str
    user_agent: str

@dataclass
class SecurityAlert(DomainEvent):
    alert_type: str
    severity: str
    metadata: Dict

@dataclass
class PasswordChanged(DomainEvent):
    pass

@dataclass
class TwoFactorEnabled(DomainEvent):
    pass

@dataclass
class TwoFactorDisabled(DomainEvent):
    reason: str