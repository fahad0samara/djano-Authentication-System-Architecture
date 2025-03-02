from django.utils import timezone
from datetime import timedelta
from .models import FailedLoginAttempt

class LoginAttemptMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/login/' and request.method == 'POST':
            username = request.POST.get('username')
            ip = self.get_client_ip(request)
            
            # Check for too many failed attempts
            attempts = FailedLoginAttempt.objects.filter(
                username=username,
                ip_address=ip,
                timestamp__gte=timezone.now() - timedelta(minutes=15)
            ).first()
            
            if attempts and attempts.attempt_count >= 5:
                return self.block_request(request)
        
        return self.get_response(request)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')