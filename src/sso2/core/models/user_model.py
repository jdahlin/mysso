from django.contrib.auth.models import AbstractUser
from django.db.models import CASCADE, DateTimeField, ForeignKey


class User(AbstractUser):
    tenant = ForeignKey("core.Tenant", on_delete=CASCADE, null=True)

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
