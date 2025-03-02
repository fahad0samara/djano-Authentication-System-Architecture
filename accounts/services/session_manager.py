from typing import List
from django.contrib.sessions.models import Session
from django.utils import timezone
from ..models import KnownDevice
from .device_fingerprint_service import DeviceFingerprintService

class SessionManager:
    @staticmethod
    def list_active_sessions(user_id: int) -> List[dict]:
        """List all active sessions for a user."""
        sessions = Session.objects.filter(
            expire_date__gt=timezone.now()
        )
        
        active_sessions = []
        for session in sessions:
            data = session.get_decoded()
            if str(data.get('_auth_user_id')) == str(user_id):
                device = KnownDevice.objects.filter(
                    fingerprint=data.get('device_fingerprint')
                ).first()
                
                active_sessions.append({
                    'session_key': session.session_key,
                    'device_name': device.name if device else 'Unknown Device',
                    'last_activity': session.expire_date - timezone.timedelta(weeks=2)
                })
                
        return active_sessions
    
    @staticmethod
    def revoke_session(session_key: str) -> None:
        """Revoke a specific session."""
        Session.objects.filter(session_key=session_key).delete()