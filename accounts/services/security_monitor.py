from typing import Dict, Optional, List
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.core.cache import cache
from ..models import LoginHistory, UserActivity
from .notification_service import NotificationService
from ..utils.validators import validate_user_id

class SecurityMonitor:
    CACHE_PREFIX = "security_monitor:"
    CACHE_TIMEOUT = 3600  # 1 hour
    
    @staticmethod
    def check_suspicious_activity(user_id: int) -> Optional[Dict]:
        """
        Monitor for suspicious account activity.
        
        Args:
            user_id: The ID of the user to check
            
        Returns:
            Optional[Dict]: Risk assessment results if suspicious activity found
            
        Raises:
            ValidationError: If user_id is invalid
        """
        try:
            validate_user_id(user_id)
            
            # Try to get from cache first
            cache_key = f"{SecurityMonitor.CACHE_PREFIX}activity:{user_id}"
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Check for multiple failed logins using a single query
            recent_activity = SecurityMonitor._get_recent_activity(user_id)
            
            risk_factors = SecurityMonitor._analyze_risk_factors(recent_activity)
            
            if risk_factors["risk_level"] == "high":
                NotificationService.send_security_alert(
                    user_id,
                    "suspicious_activity",
                    risk_factors
                )
                
                # Cache the result
                cache.set(cache_key, risk_factors, SecurityMonitor.CACHE_TIMEOUT)
                return risk_factors
            
            return None
            
        except ValidationError as e:
            raise
        except Exception as e:
            # Log the error but don't expose internal details
            logger.error(f"Error checking suspicious activity: {str(e)}")
            return None
    
    @staticmethod
    def _get_recent_activity(user_id: int) -> Dict:
        """Get recent user activity in a single query."""
        now = timezone.now()
        yesterday = now - timedelta(hours=24)
        
        # Use select_related to minimize queries
        activities = LoginHistory.objects.filter(
            user_id=user_id,
            timestamp__gte=yesterday
        ).values('status', 'ip_address').distinct()
        
        return {
            'failed_attempts': sum(1 for a in activities if a['status'] == 'failed'),
            'unique_locations': len(set(a['ip_address'] for a in activities))
        }
    
    @staticmethod
    def _analyze_risk_factors(activity: Dict) -> Dict:
        """Analyze activity data for risk factors."""
        risk_score = 0
        risk_factors = []
        
        if activity['failed_attempts'] >= 5:
            risk_score += 40
            risk_factors.append("multiple_failed_attempts")
            
        if activity['unique_locations'] >= 3:
            risk_score += 30
            risk_factors.append("multiple_locations")
            
        # Add time-based risk factor
        current_hour = timezone.now().hour
        if current_hour < 6 or current_hour > 22:
            risk_score += 20
            risk_factors.append("unusual_time")
            
        return {
            "risk_level": "high" if risk_score >= 60 else "medium" if risk_score >= 30 else "low",
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "failed_attempts": activity['failed_attempts'],
            "unique_locations": activity['unique_locations']
        }