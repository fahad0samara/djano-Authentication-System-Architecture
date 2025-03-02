import pyotp
import secrets
from typing import List

def generate_backup_codes(count: int = 8) -> List[str]:
    """Generate a list of backup codes for 2FA recovery."""
    return [secrets.token_hex(4).upper() for _ in range(count)]

def get_totp_uri(secret: str, username: str, issuer: str = "YourApp") -> str:
    """Generate the URI for QR code generation."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(username, issuer_name=issuer)

def verify_totp(secret: str, token: str) -> bool:
    """Verify a TOTP token."""
    totp = pyotp.TOTP(secret)
    return totp.verify(token)