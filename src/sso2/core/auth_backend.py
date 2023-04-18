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
        **kwargs: dict[str, Any],
    ) -> User | None:
        if username is None or password is None:
            return None
        query_filters = kwargs
        if tenant is not None:
            query_filters["tenant"] = tenant
        try:
            user = User.objects.get(email=username, **query_filters)
        except User.DoesNotExist:
            print(f"no such user: {username} {query_filters}")
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            User().set_password(password)
        else:
            print(user)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
