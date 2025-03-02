from typing import Optional, List
from datetime import datetime
from .interfaces import UserService, AuthenticationService
from .dtos import UserDTO, LoginAttemptDTO
from ..domain.factories import UserFactory
from ..domain.exceptions import AuthenticationError
from ..infrastructure.repositories.user_repository import DjangoUserRepository
from ..services.password_service import PasswordService

class DjangoUserService(UserService):
    def __init__(self, user_repository: DjangoUserRepository):
        self.user_repository = user_repository
        self.password_service = PasswordService()
    
    def get_user_by_id(self, user_id: int) -> Optional[UserDTO]:
        return self.user_repository.find_by_id(user_id)
    
    def create_user(self, username: str, email: str, password: str) -> UserDTO:
        # Hash password
        hashed_password = self.password_service.hash_password(password)
        
        # Create user through factory
        user = UserFactory.create_user(username, email, hashed_password)
        
        # Save and return
        return self.user_repository.save(UserDTO(
            id=0,
            username=user.username,
            email=user.email.value,
            is_active=user.is_active,
            date_joined=user.date_joined,
            last_login=None,
            two_factor_enabled=False
        ))
    
    def update_user(self, user_id: int, data: dict) -> UserDTO:
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")
            
        # Update fields
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
                
        return self.user_repository.update(user)

class DjangoAuthenticationService(AuthenticationService):
    def __init__(
        self,
        user_repository: DjangoUserRepository,
        password_service: PasswordService
    ):
        self.user_repository = user_repository
        self.password_service = password_service
    
    def authenticate(self, email: str, password: str) -> Optional[UserDTO]:
        user = self.user_repository.find_by_email(email)
        if not user:
            return None
            
        if not self.password_service.verify_password(password, user.password):
            return None
            
        return user
    
    def verify_two_factor(self, user_id: int, code: str) -> bool:
        user = self.user_repository.find_by_id(user_id)
        if not user or not user.two_factor_enabled:
            return False
            
        # Verify 2FA code logic here
        return True
    
    def record_login_attempt(self, attempt: LoginAttemptDTO) -> None:
        # Record attempt in audit log
        pass