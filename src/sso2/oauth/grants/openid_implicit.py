from authlib.oauth2 import OAuth2Request
from authlib.oidc.core import OpenIDImplicitGrant, UserInfo

from sso2.core.models.user_model import User
from sso2.core.types import JwtConfig
from sso2.oauth.models.authorization_code_model import AuthorizationCode


class MyOpenIDImplicitGrant(OpenIDImplicitGrant):  # type: ignore[misc]
    TOKEN_ENDPOINT_AUTH_METHODS = [
        "client_secret_basic",
        "client_secret_jwt",
        "client_secret_post",
        "none",
        "private_key_jwt",
        # "self_signed_tls_client_auth",
        # "tls_client_auth",
    ]

    def exists_nonce(self, nonce: str, request: OAuth2Request) -> bool:
        try:
            AuthorizationCode.objects.get(client_id=request.client_id, nonce=nonce)
            return True
        except AuthorizationCode.DoesNotExist:
            return False

    def get_jwt_config(self) -> JwtConfig:
        tenant = self.client.tenant
        private_key = tenant.get_private_key()
        return {
            "key": private_key.as_dict(is_private=True, alg="RS256", use="sig"),
            "alg": "RS256",
            "iss": tenant.get_issuer(),
            "exp": 3600,
        }

    def generate_user_info(self, user: User, scope: str) -> UserInfo:
        user_info = UserInfo(sub=user.id, name=user.username)
        if "email" in scope:
            user_info["email"] = user.email
        return user_info
