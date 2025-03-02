from django.http import HttpResponseForbidden
from django.utils import timezone
from ..services.session_security_service import SessionSecurityService
from ..services.device_fingerprint_service import DeviceFingerprintService
import logging

logger = logging.getLogger(__name__)

class SessionSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                # Get request data for device fingerprinting
                request_data = {
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'accept_language': request.META.get('HTTP_ACCEPT_LANGUAGE', ''),
                    'screen_resolution': request.headers.get('X-Screen-Resolution', ''),
                    'timezone': request.headers.get('X-Timezone', ''),
                    'platform': request.headers.get('X-Platform', ''),
                    'plugins': request.headers.get('X-Plugins', ''),
                    'canvas_fingerprint': request.headers.get('X-Canvas-Fingerprint', ''),
                    'webgl_fingerprint': request.headers.get('X-WebGL-Fingerprint', '')
                }
                
                # Validate session
                validation_result = SessionSecurityService.validate_session(
                    request.session.session_key,
                    request.user.id,
                    request_data
                )
                
                if not validation_result['valid']:
                    logger.warning(
                        f"Invalid session detected: {validation_result['reason']} "
                        f"for user {request.user.id}"
                    )
                    request.session.flush()
                    return HttpResponseForbidden('Invalid session')
                
                # Enforce session limits
                SessionSecurityService.enforce_session_limits(request.user.id)
                
                # Update last activity
                request.session['last_activity'] = timezone.now().isoformat()
                
            except Exception as e:
                logger.error(f"Error in session security middleware: {str(e)}")
                return HttpResponseForbidden('Session validation error')
        
        return self.get_response(request)