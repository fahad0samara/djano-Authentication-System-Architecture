from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from .value_objects import Email, Password, DeviceFingerprint
from .events import DomainEvent, UserCreated, PasswordChanged

@dataclass
class UserAggregate:
    id: int
    username: str
    email: Email
    password: Password
    is_active: bool
    date_joined: datetime
    last_login: Optional[datetime]
    two_factor_enabled: bool
    trusted_devices: List[DeviceFingerprint]
    events: List[DomainEvent]
    
    def change_password(self, new_password: Password) -> None:
        self.password = new_password
        self.events.append(PasswordChanged(
            timestamp=datetime.now(),
            user_id=self.id
        ))
    
    def add_trusted_device(self, device: DeviceFingerprint) -> None:
        if device not in self.trusted_devices:
            self.trusted_devices.append(device)
    
    def remove_trusted_device(self, device: DeviceFingerprint) -> None:
        if device in self.trusted_devices:
            self.trusted_devices.remove(device)