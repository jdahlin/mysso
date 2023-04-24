import secrets
from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models import CASCADE, BooleanField, DateTimeField, ForeignKey

if TYPE_CHECKING:
    from sso2.core.models import Tenant


class CustomUserManager(UserManager["User"]):
    def create_user(
        self,
        username: str,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: "Tenant",
    ) -> "User":
        user = super().create_user(username, email, password, **extra_fields)
        from sso2.core.email import send_verification_email

        send_verification_email(user)
        return user


class User(AbstractUser):
    objects = CustomUserManager()  # type: ignore[assignment]

    tenant = ForeignKey("core.Tenant", on_delete=CASCADE, null=True)

    email_verified = BooleanField(default=False)

    # OpenID

    # name

    @property
    def family_name(self) -> str:
        return self.last_name

    @property
    def given_name(self) -> str:
        return self.first_name

    # middle_name
    # nickname
    # preferred_username
    # profile
    # picture
    # website
    # gender
    # birthdate
    # zoneinfo
    # locale

    updated_at = DateTimeField(auto_now=True)

    def reset_password(self) -> None:
        from sso2.core.email import send_password_reset_email

        send_password_reset_email(user=self)
        self.password = secrets.token_hex(32)
        self.save()
