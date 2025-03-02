from django.http import HttpResponseTooManyRequests
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import hashlib

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Skip rate limiting for static files
        if request.path.startswith(('/static/', '/media/')):
            return self.get_response(request)
            
        # Generate cache key based on IP and path
        key = self._generate_cache_key(request)
        
        # Check rate limit
        if not self._check_rate_limit(key, request):
            return HttpResponseTooManyRequests('Rate limit exceeded')
            
        return self.get_response(request)
        
    def _generate_cache_key(self, request):
        ip = request.META.get('REMOTE_ADDR', '')
        path = request.path
        
        # Different limits for auth endpoints
        if path.startswith('/auth/'):
            return f"ratelimit:auth:{ip}"
        return f"ratelimit:general:{ip}:{path}"
        
    def _check_rate_limit(self, key, request):
        # Stricter limits for auth endpoints
        if request.path.startswith('/auth/'):
            return self._check_auth_rate_limit(key)
        return self._check_general_rate_limit(key)
        
    def _check_auth_rate_limit(self, key):
        """Stricter rate limiting for authentication endpoints."""
        LIMIT = 5  # attempts
        WINDOW = 300  # 5 minutes
        
        attempts = cache.get(key, [])
        now = timezone.now()
        
        # Clean old attempts
        attempts = [t for t in attempts if t > now - timedelta(seconds=WINDOW)]
        
        if len(attempts) >= LIMIT:
            return False
            
        attempts.append(now)
        cache.set(key, attempts, WINDOW)
        return True
        
    def _check_general_rate_limit(self, key):
        """General rate limiting for other endpoints."""
        LIMIT = 60  # requests
        WINDOW = 60  # 1 minute
        
        count = cache.get(key, 0)
        
        if count >= LIMIT:
            return False
            
        cache.set(key, count + 1, WINDOW)
        return True