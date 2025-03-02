import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import LoginHistory
from accounts.services.security_service import SecurityService

User = get_user_model()

@pytest.mark.django_db
class TestAuthentication:
    def test_successful_login(self, client, test_user, test_password):
        """Test successful login attempt."""
        response = client.post(reverse('login'), {
            'username': test_user.username,
            'password': test_password
        })
        
        assert response.status_code == 302  # Redirect after login
        assert '_auth_user_id' in client.session
        
        # Verify login history
        history = LoginHistory.objects.filter(user=test_user).first()
        assert history is not None
        assert history.status == 'success'
    
    def test_failed_login(self, client, test_user):
        """Test failed login attempt."""
        response = client.post(reverse('login'), {
            'username': test_user.username,
            'password': 'wrong-password'
        })
        
        assert response.status_code == 200  # Stay on login page
        assert '_auth_user_id' not in client.session
        
        # Verify login history
        history = LoginHistory.objects.filter(user=test_user).first()
        assert history is not None
        assert history.status == 'failed'
    
    def test_login_rate_limiting(self, client, test_user):
        """Test rate limiting on failed login attempts."""
        for _ in range(5):
            client.post(reverse('login'), {
                'username': test_user.username,
                'password': 'wrong-password'
            })
            
        # Next attempt should be blocked
        response = client.post(reverse('login'), {
            'username': test_user.username,
            'password': 'wrong-password'
        })
        
        assert response.status_code == 403  # Forbidden due to rate limit
    
    def test_suspicious_ip_login(self, client, test_user, test_password):
        """Test login from suspicious IP."""
        client.META['REMOTE_ADDR'] = '192.168.1.1'  # Private IP
        
        response = client.post(reverse('login'), {
            'username': test_user.username,
            'password': test_password
        })
        
        # Should still allow login but mark as suspicious
        assert response.status_code == 302
        history = LoginHistory.objects.filter(user=test_user).first()
        assert history.metadata.get('suspicious') == True
    
    @pytest.mark.parametrize('password', [
        'short',  # Too short
        'nouppercasepass123',  # No uppercase
        'NOLOWERCASEPASS123',  # No lowercase
        'NoSpecialChars123',  # No special chars
        'No@Numbers',  # No numbers
    ])
    def test_password_strength_validation(self, client, password):
        """Test password strength requirements."""
        response = client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': password,
            'password2': password
        })
        
        assert response.status_code == 200  # Stay on registration page
        assert 'password' in response.context['form'].errors
        
    def test_concurrent_session_limit(self, client, test_user, test_password):
        """Test concurrent session limiting."""
        # Create multiple sessions
        sessions = []
        for _ in range(6):
            client.post(reverse('login'), {
                'username': test_user.username,
                'password': test_password
            })
            sessions.append(client.session.session_key)
            
        # Verify only 5 sessions are active
        active_sessions = Session.objects.filter(
            session_key__in=sessions,
            expire_date__gt=timezone.now()
        ).count()
        
        assert active_sessions == 5  # Maximum allowed sessions