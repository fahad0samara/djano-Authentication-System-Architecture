from django.http import HttpResponse

def add_security_headers(response: HttpResponse) -> HttpResponse:
    """Add security headers to response."""
    headers = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=()',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';",
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
    
    for header, value in headers.items():
        response[header] = value
    
    return response