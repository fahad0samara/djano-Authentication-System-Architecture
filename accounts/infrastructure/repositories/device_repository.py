from typing import List, Optional
from django.utils import timezone
from ...application.ports import DeviceRepository
from ...application.dtos import DeviceInfoDTO
from ..models import KnownDevice

class DjangoDeviceRepository(DeviceRepository):
    def save_device(self, device: DeviceInfoDTO) -> DeviceInfoDTO:
        django_device = KnownDevice.objects.create(
            name=device.name,
            fingerprint=device.fingerprint,
            last_used=device.last_used,
            is_trusted=device.is_trusted
        )
        return self._to_dto(django_device)
    
    def get_user_devices(self, user_id: int) -> List[DeviceInfoDTO]:
        devices = KnownDevice.objects.filter(user_id=user_id)
        return [self._to_dto(device) for device in devices]
    
    def find_device(self, fingerprint: str) -> Optional[DeviceInfoDTO]:
        try:
            device = KnownDevice.objects.get(fingerprint=fingerprint)
            return self._to_dto(device)
        except KnownDevice.DoesNotExist:
            return None
    
    def _to_dto(self, device: KnownDevice) -> DeviceInfoDTO:
        return DeviceInfoDTO(
            name=device.name,
            fingerprint=device.fingerprint,
            last_used=device.last_used,
            is_trusted=device.is_trusted
        )