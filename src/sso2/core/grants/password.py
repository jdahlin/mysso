from authlib.oauth2.rfc6749 import ResourceOwnerPasswordCredentialsGrant

from sso2.core.models.user_model import User


class MyPasswordGrant(ResourceOwnerPasswordCredentialsGrant):  # type: ignore[misc]
    def authenticate_user(self, username: str, password: str) -> User | None:
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass
        return None
