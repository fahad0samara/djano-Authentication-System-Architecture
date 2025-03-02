import secrets
from django.core.signing import TimestampSigner
from django.conf import settings

class TokenService:
    @staticmethod
    def generate_token(user_id: int, purpose: str) -> str:
        """Generate secure tokens for various purposes."""
        signer = TimestampSigner(salt=purpose)
        return signer.sign(str(user_id))
    
    @staticmethod
    def verify_token(token: str, purpose: str, max_age=None) -> int:
        """Verify a token and return the user_id."""
        signer = TimestampSigner(salt=purpose)
        try:
            user_id = signer.unsign(token, max_age=max_age)
            return int(user_id)
        except:
            return None
            
    @staticmethod
    def generate_backup_codes(count: int = 8) -> list:
        """Generate backup codes for 2FA."""
        return [secrets.token_hex(4).upper() for _ in range(count)]