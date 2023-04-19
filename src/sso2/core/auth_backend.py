from typing import Any

from django.contrib.auth.backends import ModelBackend
from django.http import HttpRequest

from sso2.core.models.tenant_model import Tenant
from sso2.core.models.user_model import User


class DjangoAuthBackend(ModelBackend):
    def authenticate(
        self,
        request: HttpRequest | None,
        username: str | None = None,
        password: str | None = None,
        tenant: Tenant | None = None,
        **kwargs: str | int | Tenant | None,
    ) -> User | None:
        email = kwargs.pop("email", None)
        if (username is None and email is None) or password is None:
            return None
        query_filters: dict[str, Any] = kwargs
        if tenant is not None:
            query_filters["tenant"] = tenant
        try:
            user = User.objects.get(email=email, **query_filters)
        except User.DoesNotExist:
            print(f"no such user: {email} {query_filters}")
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            User().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
