from django.http import HttpResponseBadRequest, HttpResponse
from django.core.exceptions import ValidationError
import json

class ApiSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if request.path.startswith('/api/'):
            # Validate content type
            if request.method in ['POST', 'PUT', 'PATCH']:
                content_type = request.headers.get('Content-Type', '')
                if not content_type.startswith('application/json'):
                    return HttpResponse(
                        'Unsupported Media Type',
                        status=415
                    )
                    
                # Validate JSON format
                try:
                    if request.body:
                        json.loads(request.body)
                except json.JSONDecodeError:
                    return HttpResponseBadRequest('Invalid JSON format')
                    
            # Validate request size
            if request.META.get('CONTENT_LENGTH'):
                if int(request.META['CONTENT_LENGTH']) > 10 * 1024 * 1024:  # 10MB
                    return HttpResponse(
                        'Request Entity Too Large',
                        status=413
                    )
                    
            # Validate query parameters
            try:
                self._validate_query_params(request.GET)
            except ValidationError as e:
                return HttpResponseBadRequest(str(e))
                
        return self.get_response(request)
        
    def _validate_query_params(self, params):
        """Validate query parameters for potential SQL injection."""
        sql_patterns = [
            'SELECT', 'INSERT', 'UPDATE', 'DELETE',
            'DROP', 'UNION', 'ALTER', 'EXEC',
            '--', ';', '/*', '*/'
        ]
        
        for value in params.values():
            if any(pattern.lower() in value.lower() for pattern in sql_patterns):
                raise ValidationError('Invalid query parameters')