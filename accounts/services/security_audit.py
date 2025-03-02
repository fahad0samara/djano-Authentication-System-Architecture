from typing import Dict, Any
from django.http import HttpRequest
from ..utils.ip import get_client_ip, is_ip_private, get_country_code
from ..utils.device import parse_user_agent

class SecurityAuditService:
    @staticmethod
    def audit_login_attempt(request: HttpRequest, username: str, success: bool) -> Dict[str, Any]:
        """Audit login attempts for security monitoring."""
        ip = get_client_ip(request)
        device_info = parse_user_agent(request)
        
        return {
            'timestamp': timezone.now(),
            'username': username,
            'ip_address': ip,
            'country': get_country_code(ip),
            'is_private_ip': is_ip_private(ip),
            'user_agent': device_info,
            'success': success,
            'path': request.path,
            'method': request.method,
            'headers': dict(request.headers)
        }