from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class UserDTO:
    id: int
    username: str
    email: str
    is_active: bool
    date_joined: datetime
    last_login: Optional[datetime]
    two_factor_enabled: bool

@dataclass
class LoginAttemptDTO:
    timestamp: datetime
    ip_address: str
    user_agent: str
    status: str

@dataclass
class SecurityAuditDTO:
    timestamp: datetime
    action: str
    ip_address: str
    metadata: dict

@dataclass
class DeviceInfoDTO:
    name: str
    fingerprint: str
    last_used: datetime
    is_trusted: bool