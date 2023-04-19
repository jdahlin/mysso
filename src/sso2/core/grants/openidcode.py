from authlib.oauth2 import OAuth2Request
from authlib.oidc.core import OpenIDCode, UserInfo
from django.conf import settings

import sso2.conftest
from sso2.core.grants.authorization_code import MyAuthorizationCodeGrant
from sso2.core.models.authorization_code_model import AuthorizationCode
from sso2.core.models.user_model import User
from sso2.core.types import JwtConfig


class MyOpenIDCode(OpenIDCode):  # type: ignore[misc]
    def exists_nonce(self, nonce: str, request: OAuth2Request) -> bool:
        return AuthorizationCode.exists_nonce(nonce, request.client_id)

    def get_jwt_config(self, grant: MyAuthorizationCodeGrant) -> JwtConfig:
        tenant = sso2.conftest.tenant
        private_key = tenant.get_private_key()
        return {
            "key": private_key.as_dict(is_private=True, alg="RS256", use="sig"),
            "alg": "RS256",
            "iss": settings.APP_HOST,
            "tid": str(tenant.id),
            "exp": 3600,
        }

    def generate_user_info(self, user: User, scope: str) -> UserInfo:
        user_info = UserInfo(sub=str(user.pk), name=user.username)
        if "email" in scope:
            user_info["email"] = user.email
        if "profile" in scope:
            user_info["first_name"] = user.first_name
            user_info["last_name"] = user.last_name
        return user_info
