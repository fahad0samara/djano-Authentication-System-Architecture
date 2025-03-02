import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import ipaddress

def validate_password_strength(password: str) -> None:
    """Validate password meets strength requirements."""
    if len(password) < 10:
        raise ValidationError(_('Password must be at least 10 characters long.'))
        
    if not re.search(r'[A-Z]', password):
        raise ValidationError(_('Password must contain at least one uppercase letter.'))
        
    if not re.search(r'[a-z]', password):
        raise ValidationError(_('Password must contain at least one lowercase letter.'))
        
    if not re.search(r'[0-9]', password):
        raise ValidationError(_('Password must contain at least one number.'))
        
    if not re.search(r'[^A-Za-z0-9]', password):
        raise ValidationError(_('Password must contain at least one special character.'))

def validate_username(username: str) -> None:
    """Validate username format."""
    if not username:
        raise ValidationError(_('Username cannot be empty.'))
        
    if not re.match(r'^[a-zA-Z0-9_-]{3,30}$', username):
        raise ValidationError(_('Username must be 3-30 characters and contain only letters, numbers, underscores, and hyphens.'))

def validate_user_id(user_id: int) -> None:
    """Validate user ID."""
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValidationError(_('Invalid user ID.'))

def validate_ip_address(ip_address: str) -> None:
    """Validate IP address format."""
    try:
        ipaddress.ip_address(ip_address)
    except ValueError:
        raise ValidationError(_('Invalid IP address format.'))