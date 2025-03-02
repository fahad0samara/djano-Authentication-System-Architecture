import pyotp
from typing import Tuple
from ..models import CustomUser
from .token_service import TokenService

class MFAService:
    @staticmethod
    def setup_mfa(user: CustomUser) -> Tuple[str, str]:
        """Set up MFA for a user."""
        secret = pyotp.random_base32()
        backup_codes = TokenService.generate_backup_codes()
        
        return secret, backup_codes
    
    @staticmethod
    def verify_code(secret: str, code: str) -> bool:
        """Verify MFA code."""
        totp = pyotp.TOTP(secret)
        return totp.verify(code)
    
    @staticmethod
    def get_qr_uri(secret: str, email: str) -> str:
        """Generate QR code URI for MFA setup."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(email, issuer_name="SecureApp")