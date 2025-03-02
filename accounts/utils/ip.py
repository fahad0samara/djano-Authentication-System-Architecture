import ipaddress
from typing import Optional
from django.http import HttpRequest

def get_client_ip(request: HttpRequest) -> str:
    """Get client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def is_ip_private(ip: str) -> bool:
    """Check if IP address is private."""
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return True

def get_country_code(ip: str) -> Optional[str]:
    """Get country code from IP address using GeoIP2."""
    try:
        from django.contrib.gis.geoip2 import GeoIP2
        g = GeoIP2()
        return g.country_code(ip)
    except:
        return None