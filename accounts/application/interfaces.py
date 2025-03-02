from abc import ABC, abstractmethod
from typing import Optional
from .dtos import UserDTO, LoginAttemptDTO

class UserService(ABC):
    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[UserDTO]:
        pass
    
    @abstractmethod
    def create_user(self, username: str, email: str, password: str) -> UserDTO:
        pass
    
    @abstractmethod
    def update_user(self, user_id: int, data: dict) -> UserDTO:
        pass

class AuthenticationService(ABC):
    @abstractmethod
    def authenticate(self, email: str, password: str) -> Optional[UserDTO]:
        pass
    
    @abstractmethod
    def verify_two_factor(self, user_id: int, code: str) -> bool:
        pass
    
    @abstractmethod
    def record_login_attempt(self, attempt: LoginAttemptDTO) -> None:
        pass