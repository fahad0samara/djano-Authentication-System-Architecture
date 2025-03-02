from typing import List, Optional
from django.utils import timezone
from ..models import KnownDevice
from .device_fingerprint_service import DeviceFingerprintService
from .notification_service import NotificationService

class DeviceManager:
    @staticmethod
    def register_device(user_id: int, fingerprint: str, device_info: dict) -> KnownDevice:
        """Register a new device for a user."""
        device = KnownDevice.objects.create(
            user_id=user_id,
            fingerprint=fingerprint,
            name=f"{device_info.get('browser')} on {device_info.get('os')}",
            last_used=timezone.now()
        )
        
        NotificationService.send_security_alert(
            user_id,
            "new_device",
            {"device_name": device.name}
        )
        
        return device
    
    @staticmethod
    def verify_device(user_id: int, fingerprint: str) -> Optional[KnownDevice]:
        """Verify if device is known and trusted."""
        return KnownDevice.objects.filter(
            user_id=user_id,
            fingerprint=fingerprint,
            is_trusted=True
        ).first()
        
    @staticmethod
    def list_devices(user_id: int) -> List[KnownDevice]:
        """List all devices registered to a user."""
        return KnownDevice.objects.filter(
            user_id=user_id
        ).order_by('-last_used')