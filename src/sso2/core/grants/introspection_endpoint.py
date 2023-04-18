from typing import TypedDict, cast

from authlib.oauth2 import OAuth2Request
from authlib.oauth2.rfc7662 import IntrospectionEndpoint

from sso2.core.models.oauth2_client_model import OAuth2Client
from sso2.core.models.oauth2_token_model import OAuth2Token


class IntrospectedToken(TypedDict):
    active: bool
    client_id: str
    token_type: str
    username: str | None
    scope: str
    sub: int | None
    aud: str
    iss: str
    exp: int
    iat: int


class MyIntrospectionEndpoint(IntrospectionEndpoint):  # type: ignore[misc]
    def query_token(self, token: str, token_type_hint: str) -> OAuth2Token:
        if token_type_hint == "access_token":  # noqa: S105
            tok = OAuth2Token.objects.filter(access_token=token).first()
        elif token_type_hint == "refresh_token":  # noqa: S105
            tok = OAuth2Token.objects.filter(refresh_token=token).first()
        else:
            # without token_type_hint
            tok = OAuth2Token.objects.filter(access_token=token).first()
            if not tok:
                tok = OAuth2Token.objects.filter(refresh_token=token).first()
        return cast(OAuth2Token, tok)

    def introspect_token(self, token: OAuth2Token) -> IntrospectedToken:
        sub = None
        username = None
        if token.user:
            sub = token.user.id
            username = token.user.username
        return {
            "active": True,
            "client_id": token.client_id,
            "token_type": token.token_type,
            "username": username,
            "scope": token.get_scope(),
            "sub": sub,
            "aud": token.client_id,
            "iss": "https://server.example.com/",
            "exp": token.get_expires_at(),
            "iat": token.issued_at,
        }

    def check_permission(
        self,
        token: str,
        client: OAuth2Client,
        request: OAuth2Request,
    ) -> bool:
        return True
