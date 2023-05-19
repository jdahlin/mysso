from authlib.oauth2.rfc6749 import ResourceOwnerPasswordCredentialsGrant

from sso2.core.models import Tenant
from sso2.core.models.user_model import User


class MyPasswordGrant(ResourceOwnerPasswordCredentialsGrant):  # type: ignore[misc]
    TOKEN_ENDPOINT_AUTH_METHODS = ["client_secret_basic", "client_secret_post"]

    def authenticate_user(self, username: str, password: str) -> User | None:
        tenant_id = self.request.uri.split("/")[4]
        tenant = Tenant.get_or_404(tenant_id=tenant_id)

        try:
            user = User.objects.get(username=username, tenant=tenant)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass
        return None
