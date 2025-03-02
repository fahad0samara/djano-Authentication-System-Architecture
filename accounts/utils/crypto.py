from cryptography.fernet import Fernet
from django.conf import settings
from base64 import b64encode, b64decode

class CryptoUtil:
    @staticmethod
    def generate_key() -> bytes:
        """Generate a new encryption key."""
        return Fernet.generate_key()
    
    @staticmethod
    def encrypt(data: str) -> str:
        """Encrypt sensitive data."""
        f = Fernet(settings.ENCRYPTION_KEY)
        return b64encode(f.encrypt(data.encode())).decode()
    
    @staticmethod
    def decrypt(encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        f = Fernet(settings.ENCRYPTION_KEY)
        return f.decrypt(b64decode(encrypted_data)).decode()