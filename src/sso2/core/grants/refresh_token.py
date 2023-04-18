from authlib.oauth2.rfc6749 import RefreshTokenGrant

from sso2.core.models.oauth2_token_model import OAuth2Token
from sso2.core.models.user_model import User


class MyRefreshTokenGrant(RefreshTokenGrant):  # type: ignore[misc]
    def authenticate_refresh_token(
        self,
        refresh_token: OAuth2Token,
    ) -> OAuth2Token | None:
        try:
            item = OAuth2Token.objects.get(refresh_token=refresh_token)
            if item.is_refresh_token_active():
                return item
        except OAuth2Token.DoesNotExist:
            pass
        return None

    def authenticate_user(self, credential: OAuth2Token) -> User | None:
        return credential.user

    def revoke_old_credential(self, credential: OAuth2Token) -> None:
        credential.revoked = True
        credential.save()
