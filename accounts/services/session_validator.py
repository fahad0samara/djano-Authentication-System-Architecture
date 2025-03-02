from typing import Dict, Optional
from django.utils import timezone
from datetime import timedelta
from django.contrib.sessions.models import Session
from ..models import UserActivity
from .risk_analyzer import RiskAnalyzer

class SessionValidator:
    @staticmethod
    def validate_session(session_key: str, user_id: int, ip_address: str) -> Dict:
        """Validate session integrity and security."""
        session = Session.objects.filter(session_key=session_key).first()
        if not session:
            return {"valid": False, "reason": "session_not_found"}
            
        # Check session age
        age = timezone.now() - (session.expire_date - timedelta(weeks=2))
        if age > timedelta(hours=12):
            return {"valid": False, "reason": "session_expired"}
            
        # Check for suspicious activity
        recent_activity = UserActivity.objects.filter(
            user_id=user_id,
            action="page_view",
            timestamp__gte=timezone.now() - timedelta(minutes=5)
        ).count()
        
        if recent_activity > 100:
            return {"valid": False, "reason": "suspicious_activity"}
            
        # Analyze risk
        risk = RiskAnalyzer.analyze_login_risk(user_id, ip_address, None)
        if risk["risk_level"] == "high":
            return {"valid": False, "reason": "high_risk"}
            
        return {"valid": True}