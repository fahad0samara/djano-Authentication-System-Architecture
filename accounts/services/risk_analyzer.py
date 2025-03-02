from typing import Dict
from django.utils import timezone
from datetime import timedelta
from ..models import LoginHistory, UserActivity
from ..utils.ip import is_ip_private, get_country_code

class RiskAnalyzer:
    @staticmethod
    def analyze_login_risk(user_id: int, ip_address: str, user_agent: str) -> Dict:
        """Analyze risk level of a login attempt."""
        risk_factors = []
        risk_score = 0
        
        # Check IP reputation
        if is_ip_private(ip_address):
            risk_factors.append("private_ip")
            risk_score += 20
            
        # Check login patterns
        recent_logins = LoginHistory.objects.filter(
            user_id=user_id,
            status='success',
            timestamp__gte=timezone.now() - timedelta(days=30)
        )
        
        # New location
        known_locations = set(recent_logins.values_list('ip_address', flat=True))
        if ip_address not in known_locations:
            risk_factors.append("new_location")
            risk_score += 30
            
        # Unusual time
        current_hour = timezone.now().hour
        if current_hour < 6 or current_hour > 22:
            risk_factors.append("unusual_time")
            risk_score += 15
            
        return {
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "risk_level": "high" if risk_score > 60 else "medium" if risk_score > 30 else "low"
        }