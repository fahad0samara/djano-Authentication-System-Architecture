from typing import Optional
from django.http import HttpRequest
from django.contrib.sessions.models import Session
from django.utils import timezone

class SessionService:
    @staticmethod
    def get_active_sessions(user_id: int) -> list:
        """Get all active sessions for a user."""
        sessions = Session.objects.filter(
            expire_date__gt=timezone.now()
        )
        
        user_sessions = []
        for session in sessions:
            if str(user_id) == str(session.get_decoded().get('_auth_user_id')):
                user_sessions.append(session)
        
        return user_sessions
    
    @staticmethod
    def invalidate_all_sessions(user_id: int, except_session: Optional[str] = None) -> None:
        """Invalidate all user sessions except current."""
        sessions = SessionService.get_active_sessions(user_id)
        for session in sessions:
            if not except_session or session.session_key != except_session:
                session.delete()