import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser
import json

@pytest.mark.django_db
class TestApiSecurity:
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def auth_headers(self, test_user):
        client = APIClient()
        response = client.post(reverse('api-token'), {
            'username': test_user.username,
            'password': 'testpass123!'
        })
        token = response.data['token']
        return {'Authorization': f'Bearer {token}'}
    
    def test_rate_limiting(self, api_client):
        """Test API rate limiting."""
        endpoint = reverse('api-login')
        
        # Make multiple requests
        for _ in range(10):
            api_client.post(endpoint, {
                'username': 'test',
                'password': 'test'
            })
            
        # Next request should be rate limited
        response = api_client.post(endpoint, {
            'username': 'test',
            'password': 'test'
        })
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    
    def test_invalid_token(self, api_client):
        """Test invalid authentication token."""
        headers = {'Authorization': 'Bearer invalid-token'}
        response = api_client.get(
            reverse('api-profile'),
            headers=headers
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_expired_token(self, api_client, auth_headers):
        """Test expired token handling."""
        # Modify token to be expired
        token = auth_headers['Authorization'].split()[1]
        payload = token.split('.')[1]
        decoded = json.loads(base64.b64decode(payload + '=='))
        decoded['exp'] = int(time.time()) - 3600
        
        modified_token = create_test_token(decoded)
        headers = {'Authorization': f'Bearer {modified_token}'}
        
        response = api_client.get(
            reverse('api-profile'),
            headers=headers
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_csrf_protection(self, api_client):
        """Test CSRF protection for session-based endpoints."""
        response = api_client.post(
            reverse('api-update-profile'),
            {'name': 'test'},
            HTTP_X_CSRFTOKEN='invalid'
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_content_type_validation(self, api_client, auth_headers):
        """Test content type validation."""
        response = api_client.post(
            reverse('api-update-profile'),
            data='invalid-json',
            content_type='application/invalid',
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    
    def test_request_size_limit(self, api_client, auth_headers):
        """Test request size limiting."""
        large_data = {'data': 'x' * (11 * 1024 * 1024)}  # 11MB
        response = api_client.post(
            reverse('api-update-profile'),
            data=large_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    
    def test_sql_injection_protection(self, api_client, auth_headers):
        """Test SQL injection protection."""
        injection_attempts = [
            "' OR '1'='1",
            "; DROP TABLE users--",
            "' UNION SELECT * FROM users--",
            "1; SELECT * FROM users",
        ]
        
        for attempt in injection_attempts:
            response = api_client.get(
                reverse('api-search-users'),
                {'q': attempt},
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_method_not_allowed(self, api_client, auth_headers):
        """Test method not allowed handling."""
        response = api_client.delete(
            reverse('api-profile'),
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_invalid_json(self, api_client, auth_headers):
        """Test invalid JSON handling."""
        response = api_client.post(
            reverse('api-update-profile'),
            data='{invalid:json}',
            content_type='application/json',
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST