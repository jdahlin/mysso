from authlib.oauth2 import OAuth2Request
from authlib.oidc.core import OpenIDHybridGrant, UserInfo

from sso2.core.models.authorization_code_model import AuthorizationCode
from sso2.core.models.user_model import User
from sso2.core.types import JwtConfig


class MyOpenIDHybridGrant(OpenIDHybridGrant):  # type: ignore[misc]
    def save_authorization_code(
        self,
        code: str,
        request: OAuth2Request,
    ) -> AuthorizationCode:
        # openid request MAY have "nonce" parameter
        nonce = request.data.get("nonce")
        client = request.client
        auth_code = AuthorizationCode(
            code=code,
            client_id=client.client_id,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user=request.user,
            nonce=nonce,
        )
        auth_code.save()
        return auth_code

    def exists_nonce(self, nonce: str, request: OAuth2Request) -> bool:
        try:
            AuthorizationCode.objects.get(client_id=request.client_id, nonce=nonce)
            return True
        except AuthorizationCode.DoesNotExist:
            return False

    def get_jwt_config(self) -> JwtConfig:
        tenant = self.request.client.tenant
        private_key = tenant.get_private_key()
        return {
            "key": private_key.as_dict(is_private=True, alg="RS512", use="sig"),
            "alg": "RS512",
            "iss": "https://example.com",
            "exp": 3600,
            "tid": str(tenant.id),
        }

    def generate_user_info(self, user: User, scope: str) -> UserInfo:
        user_info = UserInfo(sub=user.id, name=user.username)
        if "email" in scope:
            user_info["email"] = user.email
        return user_info
