from django.http import HttpResponseBadRequest
import re
import html

class XSSProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Check for XSS in GET parameters
        if not self._validate_parameters(request.GET):
            return HttpResponseBadRequest('Invalid request parameters')
            
        # Check for XSS in POST data
        if request.method == 'POST':
            if not self._validate_parameters(request.POST):
                return HttpResponseBadRequest('Invalid request data')
                
        response = self.get_response(request)
        
        # Add security headers
        response['X-XSS-Protection'] = '1; mode=block'
        response['Content-Security-Policy'] = self._get_csp_policy()
        
        return response
        
    def _validate_parameters(self, parameters):
        """Check for XSS patterns in parameters."""
        xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'onerror=',
            r'onload=',
            r'onclick=',
            r'onmouseover=',
            r'onfocus=',
            r'onblur=',
            r'alert\s*\(',
            r'eval\s*\(',
            r'document\.cookie',
            r'document\.write',
            r'document\.location',
            r'<iframe',
            r'<embed',
            r'<object',
            r'data:text/html',
            r'vbscript:',
        ]
        
        pattern = '|'.join(xss_patterns)
        
        for value in parameters.values():
            if isinstance(value, str):
                # Check for XSS patterns
                if re.search(pattern, value, re.IGNORECASE):
                    return False
                    
                # Check for encoded XSS attempts
                decoded = html.unescape(value)
                if re.search(pattern, decoded, re.IGNORECASE):
                    return False
                    
        return True
        
    def _get_csp_policy(self):
        """Generate Content Security Policy."""
        directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "img-src 'self' data: https:",
            "font-src 'self' https://cdn.jsdelivr.net",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "form-action 'self'",
            "base-uri 'self'",
            "object-src 'none'"
        ]
        
        return '; '.join(directives)