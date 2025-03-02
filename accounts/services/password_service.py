import bcrypt
from typing import Tuple
from django.contrib.auth.hashers import make_password, check_password
from ..utils.validators import validate_password_strength

class PasswordService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using Django's password hasher."""
        validate_password_strength(password)
        return make_password(password)
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against stored hash."""
        return check_password(password, hashed)
    
    @staticmethod
    def generate_salt() -> str:
        """Generate a secure salt for password hashing."""
        return bcrypt.gensalt().decode('utf-8')