from authlib.oauth2 import OAuth2Request
from authlib.oidc.core import OpenIDImplicitGrant, UserInfo

from sso2.core.keyutils import get_private_key_from_path
from sso2.core.models.authorization_code_model import AuthorizationCode
from sso2.core.models.user_model import User
from sso2.core.types import JwtConfig


class MyOpenIDImplicitGrant(OpenIDImplicitGrant):  # type: ignore[misc]
    def exists_nonce(self, nonce: str, request: OAuth2Request) -> bool:
        try:
            AuthorizationCode.objects.get(client_id=request.client_id, nonce=nonce)
            return True
        except AuthorizationCode.DoesNotExist:
            return False

    def get_jwt_config(self) -> JwtConfig:
        private_key = get_private_key_from_path("master-private_key.pem")
        return {
            "key": private_key.as_dict(is_private=True, alg="RS256", use="sig"),
            "alg": "RS256",
            "iss": "https://example.com",
            "exp": 3600,
        }

    def generate_user_info(self, user: User, scope: str) -> UserInfo:
        user_info = UserInfo(sub=user.id, name=user.username)
        if "email" in scope:
            user_info["email"] = user.email
        return user_info
