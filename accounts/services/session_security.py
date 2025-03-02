from typing import List, Optional
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta
from ..models import UserActivity
from .device_manager import DeviceManager

class SessionSecurityService:
    @staticmethod
    def enforce_concurrent_sessions(user_id: int, max_sessions: int = 5) -> None:
        """Enforce maximum number of concurrent sessions."""
        sessions = Session.objects.filter(
            expire_date__gt=timezone.now()
        )
        
        user_sessions = []
        for session in sessions:
            data = session.get_decoded()
            if str(data.get('_auth_user_id')) == str(user_id):
                user_sessions.append(session)
        
        # If too many sessions, remove oldest
        if len(user_sessions) > max_sessions:
            user_sessions.sort(key=lambda s: s.expire_date)
            for session in user_sessions[:(len(user_sessions) - max_sessions)]:
                session.delete()
    
    @staticmethod
    def track_session_activity(session_key: str, user_id: int, request_path: str) -> None:
        """Track session activity for security monitoring."""
        UserActivity.objects.create(
            user_id=user_id,
            action="page_view",
            metadata={
                "path": request_path,
                "session_key": session_key
            }
        )
    
    @staticmethod
    def get_active_sessions(user_id: int) -> List[dict]:
        """Get details of all active sessions."""
        sessions = Session.objects.filter(
            expire_date__gt=timezone.now()
        )
        
        active_sessions = []
        for session in sessions:
            data = session.get_decoded()
            if str(data.get('_auth_user_id')) == str(user_id):
                device = DeviceManager.verify_device(
                    user_id,
                    data.get('device_fingerprint', '')
                )
                
                active_sessions.append({
                    "session_key": session.session_key,
                    "device_name": device.name if device else "Unknown Device",
                    "last_activity": session.expire_date - timedelta(weeks=2),
                    "is_current": session.session_key == data.get('session_key')
                })
        
        return active_sessions