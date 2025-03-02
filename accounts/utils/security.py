import secrets
import string

def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure token."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def constant_time_compare(val1: str, val2: str) -> bool:
    """Compare two strings in constant time."""
    if len(val1) != len(val2):
        return False
    return secrets.compare_digest(val1.encode(), val2.encode())