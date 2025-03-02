from typing import Dict, List
from django.utils import timezone
from datetime import timedelta
import re
from ..models import CustomUser
from .notification_service import NotificationService

class PasswordSecurityService:
    @staticmethod
    def check_password_exposure(password: str) -> Dict:
        """Check if password has been exposed in known breaches."""
        # This would integrate with HaveIBeenPwned API in production
        return {
            "is_exposed": False,
            "exposure_count": 0
        }
    
    @staticmethod
    def analyze_password_strength(password: str) -> Dict:
        """Analyze password strength and provide feedback."""
        score = 0
        feedback = []
        
        # Length check
        if len(password) >= 12:
            score += 30
        elif len(password) >= 10:
            score += 20
            feedback.append("Consider using a longer password")
            
        # Complexity checks
        if re.search(r'[A-Z]', password): score += 10
        if re.search(r'[a-z]', password): score += 10
        if re.search(r'[0-9]', password): score += 10
        if re.search(r'[^A-Za-z0-9]', password): score += 10
        
        # Variety check
        unique_chars = len(set(password))
        if unique_chars >= 8:
            score += 10
        
        return {
            "score": score,
            "strength": "strong" if score >= 70 else "medium" if score >= 50 else "weak",
            "feedback": feedback
        }
    
    @staticmethod
    def enforce_password_history(user_id: int, new_password: str) -> bool:
        """Prevent reuse of recent passwords."""
        # In production, this would check against hashed password history
        return True