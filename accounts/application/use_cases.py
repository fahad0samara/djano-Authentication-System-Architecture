from typing import Optional
from datetime import datetime
from .interfaces import UserService, AuthenticationService
from .dtos import UserDTO, LoginAttemptDTO
from ..domain.exceptions import AuthenticationError, ValidationError
from ..domain.events import LoginAttempted, SecurityAlert
from ..domain.value_objects import Email, DeviceFingerprint

class UserRegistrationUseCase:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    def execute(self, username: str, email: str, password: str) -> UserDTO:
        try:
            # Validate email format
            Email(email)
            
            # Create user
            user = self.user_service.create_user(username, email, password)
            return user
            
        except ValidationError as e:
            raise ValidationError(f"Registration failed: {str(e)}")

class UserAuthenticationUseCase:
    def __init__(
        self,
        auth_service: AuthenticationService,
        security_service: SecurityService
    ):
        self.auth_service = auth_service
        self.security_service = security_service
    
    def execute(
        self,
        email: str,
        password: str,
        ip_address: str,
        user_agent: str
    ) -> UserDTO:
        try:
            # Create device fingerprint
            device = DeviceFingerprint(
                value=self.security_service.generate_fingerprint(user_agent),
                user_agent=user_agent,
                ip_address=ip_address,
                created_at=datetime.now()
            )
            
            # Attempt authentication
            user = self.auth_service.authenticate(email, password)
            
            if not user:
                self._record_failed_attempt(email, device)
                raise AuthenticationError("Invalid credentials")
            
            # Record successful login
            self._record_successful_attempt(user.id, device)
            
            return user
            
        except Exception as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}")
    
    def _record_failed_attempt(self, email: str, device: DeviceFingerprint):
        attempt = LoginAttemptDTO(
            timestamp=datetime.now(),
            ip_address=device.ip_address,
            user_agent=device.user_agent,
            status="failed"
        )
        self.auth_service.record_login_attempt(attempt)
    
    def _record_successful_attempt(self, user_id: int, device: DeviceFingerprint):
        attempt = LoginAttemptDTO(
            timestamp=datetime.now(),
            ip_address=device.ip_address,
            user_agent=device.user_agent,
            status="success"
        )
        self.auth_service.record_login_attempt(attempt)