from datetime import datetime
from typing import Optional
from .aggregates import UserAggregate
from .value_objects import Email, Password
from .events import UserCreated

class UserFactory:
    @staticmethod
    def create_user(
        username: str,
        email: str,
        hashed_password: str,
        user_id: Optional[int] = None
    ) -> UserAggregate:
        user = UserAggregate(
            id=user_id or 0,
            username=username,
            email=Email(email),
            password=Password(
                hashed_value=hashed_password,
                last_changed=datetime.now(),
                previous_hashes=[]
            ),
            is_active=True,
            date_joined=datetime.now(),
            last_login=None,
            two_factor_enabled=False,
            trusted_devices=[],
            events=[]
        )
        
        user.events.append(UserCreated(
            timestamp=datetime.now(),
            user_id=user.id,
            username=username,
            email=email
        ))
        
        return user