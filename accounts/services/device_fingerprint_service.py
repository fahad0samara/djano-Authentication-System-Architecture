from typing import Dict, Optional
import hashlib
import json
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class DeviceFingerprintService:
    # Constants for configuration
    CACHE_PREFIX = "device_fingerprint:"
    TRUSTED_DEVICE_EXPIRY = 30  # days
    MAX_TRUSTED_DEVICES = 5
    
    @staticmethod
    def generate_fingerprint(request_data: Dict) -> str:
        """
        Generate unique device fingerprint.
        
        Args:
            request_data: Dictionary containing device information
            
        Returns:
            str: Generated fingerprint
        """
        try:
            components = [
                request_data.get('user_agent', ''),
                request_data.get('accept_language', ''),
                request_data.get('screen_resolution', ''),
                request_data.get('timezone', ''),
                request_data.get('platform', ''),
                request_data.get('plugins', ''),
                request_data.get('canvas_fingerprint', ''),
                request_data.get('webgl_fingerprint', '')
            ]
            
            fingerprint = hashlib.sha256(
                json.dumps(components, sort_keys=True).encode()
            ).hexdigest()
            
            return fingerprint
            
        except Exception as e:
            logger.error(f"Error generating device fingerprint: {str(e)}")
            # Return a temporary fingerprint
            return hashlib.sha256(str(timezone.now().timestamp()).encode()).hexdigest()
    
    @staticmethod
    def is_trusted_device(user_id: int, fingerprint: str) -> bool:
        """
        Check if device is trusted for user.
        
        Args:
            user_id: The user ID to check
            fingerprint: The device fingerprint to verify
            
        Returns:
            bool: True if device is trusted
        """
        try:
            cache_key = f"{DeviceFingerprintService.CACHE_PREFIX}trusted:{user_id}"
            trusted_devices = cache.get(cache_key, {})
            
            if fingerprint in trusted_devices:
                last_seen = trusted_devices[fingerprint]
                if timezone.now() - last_seen <= timedelta(days=DeviceFingerprintService.TRUSTED_DEVICE_EXPIRY):
                    # Update last seen timestamp
                    trusted_devices[fingerprint] = timezone.now()
                    cache.set(cache_key, trusted_devices)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking trusted device: {str(e)}")
            return False
    
    @staticmethod
    def add_trusted_device(user_id: int, fingerprint: str) -> None:
        """
        Add device to user's trusted devices.
        
        Args:
            user_id: The user ID to update
            fingerprint: The device fingerprint to trust
        """
        try:
            cache_key = f"{DeviceFingerprintService.CACHE_PREFIX}trusted:{user_id}"
            trusted_devices = cache.get(cache_key, {})
            
            # Remove expired devices
            current_time = timezone.now()
            trusted_devices = {
                fp: last_seen
                for fp, last_seen in trusted_devices.items()
                if current_time - last_seen <= timedelta(days=DeviceFingerprintService.TRUSTED_DEVICE_EXPIRY)
            }
            
            # Add new device
            trusted_devices[fingerprint] = current_time
            
            # Enforce maximum devices limit
            if len(trusted_devices) > DeviceFingerprintService.MAX_TRUSTED_DEVICES:
                # Remove oldest device
                oldest_fp = min(trusted_devices.items(), key=lambda x: x[1])[0]
                del trusted_devices[oldest_fp]
            
            cache.set(cache_key, trusted_devices)
            
        except Exception as e:
            logger.error(f"Error adding trusted device: {str(e)}")
    
    @staticmethod
    def remove_trusted_device(user_id: int, fingerprint: str) -> None:
        """
        Remove device from user's trusted devices.
        
        Args:
            user_id: The user ID to update
            fingerprint: The device fingerprint to remove
        """
        try:
            cache_key = f"{DeviceFingerprintService.CACHE_PREFIX}trusted:{user_id}"
            trusted_devices = cache.get(cache_key, {})
            
            if fingerprint in trusted_devices:
                del trusted_devices[fingerprint]
                cache.set(cache_key, trusted_devices)
                
        except Exception as e:
            logger.error(f"Error removing trusted device: {str(e)}")