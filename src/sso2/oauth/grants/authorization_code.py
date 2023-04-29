from typing import cast

from authlib.oauth2 import OAuth2Request
from authlib.oauth2.rfc6749 import AuthorizationCodeGrant
from authlib.oidc.core.grants.util import validate_nonce

from sso2.core.models.user_model import User
from sso2.oauth.models.authorization_code_model import AuthorizationCode
from sso2.oauth.models.oauth2_client_model import OAuth2Client


def exists_nonce(nonce: str, request: OAuth2Request) -> bool:
    return AuthorizationCode.exists_nonce(nonce, request.client_id)


class MyAuthorizationCodeGrant(AuthorizationCodeGrant):  # type: ignore[misc]
    TOKEN_ENDPOINT_AUTH_METHODS = ["client_secret_basic", "client_secret_post", "none"]

    def validate_authorization_redirect_uri(
        self,
        request: OAuth2Request,
        client: OAuth2Client,
    ) -> str:
        redirect_uri = super().validate_authorization_redirect_uri(request, client)
        if client.require_nonce:
            validate_nonce(request, exists_nonce, required=True)
        return cast(str, redirect_uri)

    def save_authorization_code(
        self,
        code: str,
        request: OAuth2Request,
    ) -> AuthorizationCode:
        nonce = request.data.get("nonce")
        code_challenge = request.data.get("code_challenge")
        code_challenge_method = request.data.get("code_challenge_method")
        client = request.client
        auth_code = AuthorizationCode(
            code=code,
            client_id=client.client_id,
            redirect_uri=request.redirect_uri,
            response_type=request.response_type,
            scope=request.scope,
            user=request.user,
            nonce=nonce,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )
        auth_code.save()
        return auth_code

    def query_authorization_code(self, code: str, client: OAuth2Client) -> str | None:
        try:
            auth_code = AuthorizationCode.objects.get(
                code=code,
                client_id=client.client_id,
            )
        except AuthorizationCode.DoesNotExist:
            pass
        else:
            if not auth_code.is_expired():
                return auth_code
        return None

    def delete_authorization_code(self, authorization_code: AuthorizationCode) -> None:
        authorization_code.delete()

    def authenticate_user(self, authorization_code: AuthorizationCode) -> User:
        return authorization_code.user

    def is_code_challenge_required(self) -> bool:
        return cast(bool, self.request.client.require_code_challenge)
