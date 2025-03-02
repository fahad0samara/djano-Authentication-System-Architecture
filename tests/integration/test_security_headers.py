import pytest
from django.urls import reverse

def test_security_headers(client):
    """Test security headers are properly set."""
    response = client.get(reverse('login'))
    
    # Check security headers
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'DENY'
    assert response.headers.get('X-XSS-Protection') == '1; mode=block'
    assert 'Content-Security-Policy' in response.headers
    assert 'Strict-Transport-Security' in response.headers
    
    # Verify CSP directives
    csp = response.headers.get('Content-Security-Policy')
    assert "default-src 'self'" in csp
    assert "script-src" in csp
    assert "style-src" in csp
    assert "frame-ancestors 'none'" in csp
    
def test_request_size_limit(client):
    """Test large request handling."""
    large_data = 'x' * (11 * 1024 * 1024)  # 11MB
    response = client.post(reverse('login'), {'data': large_data})
    assert response.status_code == 400  # Bad Request
    
def test_content_type_validation(client):
    """Test content type validation."""
    response = client.post(
        reverse('login'),
        data='{"invalid": "json"}',
        content_type='application/invalid'
    )
    assert response.status_code == 400
    
def test_xss_protection(client):
    """Test XSS protection."""
    xss_attempts = [
        '<script>alert(1)</script>',
        'javascript:alert(1)',
        '<img src="x" onerror="alert(1)">',
        '<iframe src="javascript:alert(1)">',
        '"><script>alert(1)</script>',
    ]
    
    for attempt in xss_attempts:
        response = client.get(reverse('login'), {'q': attempt})
        assert response.status_code == 400  # Bad Request