from django.http import HttpResponseBadRequest
import re

class SQLInjectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Check query parameters
        if not self._validate_parameters(request.GET):
            return HttpResponseBadRequest('Invalid request parameters')
            
        # Check POST data
        if request.method == 'POST':
            if not self._validate_parameters(request.POST):
                return HttpResponseBadRequest('Invalid request data')
                
        return self.get_response(request)
        
    def _validate_parameters(self, parameters):
        """Check for SQL injection patterns in parameters."""
        sql_patterns = [
            r'(\s|^)(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)(\s|$)',
            r'(\s|^)(OR|AND)(\s+)(\d+|\'.*?\')(\s*)(=|>|<)',
            r'--\s*$',
            r'\b(EXEC|EXECUTE|DECLARE|CAST)\b',
            r'(;|\||&&)',
            r'/\*.*?\*/',
            r'@@[a-zA-Z_]+',
            r'\bINTO\s+OUTFILE\b'
        ]
        
        pattern = '|'.join(sql_patterns)
        
        for value in parameters.values():
            if isinstance(value, str):
                if re.search(pattern, value, re.IGNORECASE):
                    return False
                    
        return True