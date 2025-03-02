from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class User:
    id: int
    username: str
    email: str
    is_active: bool
    date_joined: datetime
    last_login: Optional[datetime]
    two_factor_enabled: bool
    
@dataclass
class LoginAttempt:
    id: int
    user_id: int
    timestamp: datetime
    ip_address: str
    user_agent: str
    status: str
    
@dataclass
class SecurityAudit:
    id: int
    user_id: int
    action: str
    timestamp: datetime
    ip_address: str
    metadata: dict