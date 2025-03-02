from abc import ABC, abstractmethod
from typing import List, Optional
from .dtos import UserDTO, SecurityAuditDTO, DeviceInfoDTO

class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[UserDTO]:
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[UserDTO]:
        pass
    
    @abstractmethod
    def save(self, user: UserDTO) -> UserDTO:
        pass
    
    @abstractmethod
    def update(self, user: UserDTO) -> UserDTO:
        pass

class SecurityAuditRepository(ABC):
    @abstractmethod
    def save_audit(self, audit: SecurityAuditDTO) -> None:
        pass
    
    @abstractmethod
    def get_user_audits(self, user_id: int, limit: int = 100) -> List[SecurityAuditDTO]:
        pass

class DeviceRepository(ABC):
    @abstractmethod
    def save_device(self, device: DeviceInfoDTO) -> DeviceInfoDTO:
        pass
    
    @abstractmethod
    def get_user_devices(self, user_id: int) -> List[DeviceInfoDTO]:
        pass
    
    @abstractmethod
    def find_device(self, fingerprint: str) -> Optional[DeviceInfoDTO]:
        pass