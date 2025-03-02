from typing import Optional
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import ipaddress

User = get_user_model()

class SecurityService:
    @staticmethod
    def is_ip_suspicious(ip_address: str) -> bool:
        """Check if IP address is suspicious (private, reserved, etc)."""
        try:
            ip = ipaddress.ip_address(ip_address)
            return ip.is_private or ip.is_reserved or ip.is_multicast
        except ValueError:
            return True
    
    @staticmethod
    def get_user_known_ips(user) -> list:
        """Get list of IPs this user has successfully logged in from."""
        return LoginHistory.objects.filter(
            user=user,
            status='success',
            timestamp__gte=timezone.now() - timedelta(days=30)
        ).values_list('ip_address', flat=True).distinct()
    
    @staticmethod
    def should_request_2fa(user, ip_address: str) -> bool:
        """Determine if 2FA should be requested based on IP history."""
        if not user.two_factor_enabled:
            return False
            
        known_ips = SecurityService.get_user_known_ips(user)
        return ip_address not in known_ips