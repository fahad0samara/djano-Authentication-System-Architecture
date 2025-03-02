from django.http import HttpResponseForbidden
from ..services.rate_limit_service import RateLimitService
from ..services.security_audit_service import SecurityAuditService
from ..utils.headers import add_security_headers

class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Rate limiting
        if not self._check_rate_limits(request):
            return HttpResponseForbidden('Rate limit exceeded')
            
        # Process request
        response = self.get_response(request)
        
        # Add security headers
        response = add_security_headers(response)
        
        return response
        
    def _check_rate_limits(self, request):
        if request.path.startswith('/api/'):
            return RateLimitService.check_rate_limit(
                key=f"api:{request.META.get('REMOTE_ADDR')}",
                max_attempts=100,
                window=3600
            )
        return True