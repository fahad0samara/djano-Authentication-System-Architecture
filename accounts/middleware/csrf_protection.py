from django.middleware.csrf import CsrfViewMiddleware
from django.http import HttpResponseForbidden
import hmac
import hashlib
from django.conf import settings
from django.utils.crypto import constant_time_compare

class EnhancedCsrfMiddleware(CsrfViewMiddleware):
    def __init__(self, get_response):
        super().__init__(get_response)
        
    def _get_token_format(self, token):
        """Check if token format is valid."""
        if not token or len(token) != 64:  # SHA-256 hex is 64 chars
            return False
            
        try:
            # Check if token is valid hexadecimal
            int(token, 16)
            return True
        except ValueError:
            return False
    
    def _get_token(self, request):
        """Get token from various sources with additional validation."""
        # Try to get token from custom header first
        token = request.headers.get('X-CSRF-Token')
        
        if not token:
            # Fall back to standard header
            token = request.headers.get('X-CSRFToken')
            
        if not token:
            # Check form data
            token = request.POST.get('csrfmiddlewaretoken')
            
        if token and self._get_token_format(token):
            return token
            
        return None
    
    def _verify_token_signature(self, token, secret):
        """Verify token signature with additional entropy."""
        if not token or not secret:
            return False
            
        expected = hmac.new(
            settings.SECRET_KEY.encode(),
            msg=secret.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        return constant_time_compare(token, expected)
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if getattr(callback, 'csrf_exempt', False):
            return None
            
        # Get the token
        token = self._get_token(request)
        if not token:
            return HttpResponseForbidden('CSRF token missing')
            
        # Get secret from session
        secret = request.session.get('csrf_secret')
        if not secret:
            return HttpResponseForbidden('CSRF secret missing')
            
        # Verify token
        if not self._verify_token_signature(token, secret):
            return HttpResponseForbidden('CSRF token invalid')
            
        return super().process_view(request, callback, callback_args, callback_kwargs)