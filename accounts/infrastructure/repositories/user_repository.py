from typing import Optional, List
from ...application.ports import UserRepository
from ...application.dtos import UserDTO
from ...domain.exceptions import ResourceNotFoundError
from ..models import CustomUser

class DjangoUserRepository(UserRepository):
    def find_by_id(self, user_id: int) -> Optional[UserDTO]:
        try:
            user = CustomUser.objects.get(id=user_id)
            return self._to_dto(user)
        except CustomUser.DoesNotExist:
            return None
    
    def find_by_email(self, email: str) -> Optional[UserDTO]:
        try:
            user = CustomUser.objects.get(email=email)
            return self._to_dto(user)
        except CustomUser.DoesNotExist:
            return None
    
    def save(self, user: UserDTO) -> UserDTO:
        django_user = CustomUser.objects.create(
            username=user.username,
            email=user.email,
            is_active=user.is_active
        )
        return self._to_dto(django_user)
    
    def update(self, user: UserDTO) -> UserDTO:
        try:
            django_user = CustomUser.objects.get(id=user.id)
            django_user.username = user.username
            django_user.email = user.email
            django_user.is_active = user.is_active
            django_user.save()
            return self._to_dto(django_user)
        except CustomUser.DoesNotExist:
            raise ResourceNotFoundError(f"User {user.id} not found")
    
    def _to_dto(self, user: CustomUser) -> UserDTO:
        return UserDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            date_joined=user.date_joined,
            last_login=user.last_login,
            two_factor_enabled=user.two_factor_enabled
        )