import pytest
from django.utils import timezone
from accounts.services.security_service import SecurityService
from accounts.services.password_service import PasswordService
from accounts.services.token_service import TokenService

def test_password_strength_validation():
    password_service = PasswordService()
    
    # Test strong password
    strong_password = "StrongPass123!@#"
    hashed = password_service.hash_password(strong_password)
    assert password_service.verify_password(strong_password, hashed)
    
    # Test weak password should raise ValidationError
    with pytest.raises(ValidationError):
        password_service.hash_password("weak")

def test_token_generation_and_verification():
    token_service = TokenService()
    user_id = 1
    purpose = "test"
    
    token = token_service.generate_token(user_id, purpose)
    assert token is not None
    
    verified_user_id = token_service.verify_token(token, purpose)
    assert verified_user_id == user_id

def test_security_service_ip_validation():
    security_service = SecurityService()
    
    # Test private IP
    assert security_service.is_ip_suspicious("192.168.1.1")
    
    # Test public IP
    assert not security_service.is_ip_suspicious("8.8.8.8")