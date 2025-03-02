from django.http import HttpResponseBadRequest
import re
from urllib.parse import urlparse

class RequestValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Validate request size
        if request.method in ['POST', 'PUT', 'PATCH']:
            if not self._validate_request_size(request):
                return HttpResponseBadRequest('Request too large')
                
        # Validate content type
        if not self._validate_content_type(request):
            return HttpResponseBadRequest('Invalid content type')
            
        # Validate headers
        if not self._validate_headers(request):
            return HttpResponseBadRequest('Invalid headers')
            
        # Validate URL
        if not self._validate_url(request):
            return HttpResponseBadRequest('Invalid URL')
            
        return self.get_response(request)
        
    def _validate_request_size(self, request):
        """Validate request body size."""
        MAX_SIZE = 10 * 1024 * 1024  # 10MB
        content_length = request.META.get('CONTENT_LENGTH')
        
        if content_length and int(content_length) > MAX_SIZE:
            return False
        return True
        
    def _validate_content_type(self, request):
        """Validate Content-Type header."""
        if request.method not in ['POST', 'PUT', 'PATCH']:
            return True
            
        content_type = request.META.get('CONTENT_TYPE', '')
        allowed_types = [
            'application/json',
            'application/x-www-form-urlencoded',
            'multipart/form-data'
        ]
        
        return any(allowed in content_type for allowed in allowed_types)
        
    def _validate_headers(self, request):
        """Validate request headers."""
        # Check for required headers
        required_headers = ['HTTP_HOST']
        for header in required_headers:
            if header not in request.META:
                return False
                
        # Validate User-Agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if len(user_agent) > 500:  # Prevent UA header abuse
            return False
            
        # Validate Referer
        referer = request.META.get('HTTP_REFERER', '')
        if referer:
            parsed = urlparse(referer)
            if parsed.scheme not in ['http', 'https']:
                return False
                
        return True
        
    def _validate_url(self, request):
        """Validate request URL."""
        path = request.path
        
        # Prevent directory traversal
        if '..' in path:
            return False
            
        # Validate path characters
        if not re.match(r'^[a-zA-Z0-9\-_/]+$', path):
            return False
            
        # Maximum URL length
        if len(request.get_full_path()) > 2000:
            return False
            
        return True