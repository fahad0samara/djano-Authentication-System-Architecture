from typing import Dict, Optional, List
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import transaction
from ..models import UserActivity
from ..utils.validators import validate_user_id, validate_ip_address
import logging
import json

logger = logging.getLogger(__name__)

class AuditLoggingService:
    # Event type constants
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    DEVICE_ADDED = "device_added"
    DEVICE_REMOVED = "device_removed"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    
    # Risk level constants
    RISK_LOW = "low"
    RISK_MEDIUM = "medium"
    RISK_HIGH = "high"
    
    @staticmethod
    def log_security_event(
        user_id: int,
        event_type: str,
        ip_address: str,
        metadata: Optional[Dict] = None,
        risk_level: str = RISK_LOW
    ) -> None:
        """
        Log a security-related event.
        
        Args:
            user_id: The ID of the user associated with the event
            event_type: The type of security event
            ip_address: The IP address associated with the event
            metadata: Additional event-specific data
            risk_level: Risk level of the event
            
        Raises:
            ValidationError: If input validation fails
        """
        try:
            # Validate inputs
            validate_user_id(user_id)
            validate_ip_address(ip_address)
            
            if risk_level not in [AuditLoggingService.RISK_LOW, 
                                AuditLoggingService.RISK_MEDIUM, 
                                AuditLoggingService.RISK_HIGH]:
                raise ValidationError("Invalid risk level")
            
            # Ensure metadata is JSON serializable
            if metadata:
                try:
                    json.dumps(metadata)
                except (TypeError, ValueError):
                    logger.warning("Invalid metadata format, converting to string")
                    metadata = {"raw_data": str(metadata)}
            
            # Create activity record
            with transaction.atomic():
                UserActivity.objects.create(
                    user_id=user_id,
                    action=event_type,
                    ip_address=ip_address,
                    metadata=metadata or {},
                    risk_level=risk_level,
                    timestamp=timezone.now()
                )
                
        except ValidationError as e:
            raise
        except Exception as e:
            logger.error(f"Error logging security event: {str(e)}")
            # Re-raise as validation error to hide internal details
            raise ValidationError("Failed to log security event")
    
    @staticmethod
    def get_user_activity(
        user_id: int,
        start_date: Optional[timezone.datetime] = None,
        end_date: Optional[timezone.datetime] = None,
        event_types: Optional[List[str]] = None,
        risk_levels: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Retrieve user activity logs with filtering.
        
        Args:
            user_id: The ID of the user to query
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            event_types: Optional list of event types to include
            risk_levels: Optional list of risk levels to include
            limit: Maximum number of records to return
            
        Returns:
            List of activity records
            
        Raises:
            ValidationError: If input validation fails
        """
        try:
            validate_user_id(user_id)
            
            # Build query
            query = UserActivity.objects.filter(user_id=user_id)
            
            if start_date:
                query = query.filter(timestamp__gte=start_date)
            if end_date:
                query = query.filter(timestamp__lte=end_date)
            if event_types:
                query = query.filter(action__in=event_types)
            if risk_levels:
                query = query.filter(risk_level__in=risk_levels)
            
            # Get records
            activities = query.order_by('-timestamp')[:limit]
            
            # Format response
            return [
                {
                    "event_type": activity.action,
                    "timestamp": activity.timestamp,
                    "ip_address": activity.ip_address,
                    "risk_level": activity.risk_level,
                    "metadata": activity.metadata
                }
                for activity in activities
            ]
            
        except ValidationError as e:
            raise
        except Exception as e:
            logger.error(f"Error retrieving user activity: {str(e)}")
            raise ValidationError("Failed to retrieve activity logs")
    
    @staticmethod
    def analyze_user_risk(user_id: int, hours: int = 24) -> Dict:
        """
        Analyze user activity for risk assessment.
        
        Args:
            user_id: The ID of the user to analyze
            hours: Number of hours of history to analyze
            
        Returns:
            Dict containing risk analysis results
            
        Raises:
            ValidationError: If input validation fails
        """
        try:
            validate_user_id(user_id)
            
            start_time = timezone.now() - timedelta(hours=hours)
            activities = UserActivity.objects.filter(
                user_id=user_id,
                timestamp__gte=start_time
            )
            
            # Analyze risk factors
            failed_logins = activities.filter(
                action=AuditLoggingService.LOGIN_FAILED
            ).count()
            
            suspicious_events = activities.filter(
                risk_level__in=[AuditLoggingService.RISK_MEDIUM, 
                              AuditLoggingService.RISK_HIGH]
            ).count()
            
            unique_ips = activities.values('ip_address').distinct().count()
            
            # Calculate risk score
            risk_score = 0
            risk_factors = []
            
            if failed_logins >= 5:
                risk_score += 30
                risk_factors.append("multiple_failed_logins")
                
            if suspicious_events >= 3:
                risk_score += 30
                risk_factors.append("suspicious_events_detected")
                
            if unique_ips >= 3:
                risk_score += 20
                risk_factors.append("multiple_ip_addresses")
            
            # Determine overall risk level
            if risk_score >= 60:
                risk_level = AuditLoggingService.RISK_HIGH
            elif risk_score >= 30:
                risk_level = AuditLoggingService.RISK_MEDIUM
            else:
                risk_level = AuditLoggingService.RISK_LOW
            
            return {
                "risk_level": risk_level,
                "risk_score": risk_score,
                "risk_factors": risk_factors,
                "analysis_period_hours": hours,
                "failed_logins": failed_logins,
                "suspicious_events": suspicious_events,
                "unique_ip_addresses": unique_ips
            }
            
        except ValidationError as e:
            raise
        except Exception as e:
            logger.error(f"Error analyzing user risk: {str(e)}")
            raise ValidationError("Failed to analyze user risk")