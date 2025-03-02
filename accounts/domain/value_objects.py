from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class Email:
    value: str
    
    def __post_init__(self):
        if not '@' in self.value:
            raise ValidationError("Invalid email format")

@dataclass(frozen=True)
class Password:
    hashed_value: str
    last_changed: datetime
    previous_hashes: list[str]

@dataclass(frozen=True)
class DeviceFingerprint:
    value: str
    user_agent: str
    ip_address: str
    created_at: datetime

@dataclass(frozen=True)
class SecurityToken:
    value: str
    purpose: str
    expires_at: datetime
    is_used: bool = False