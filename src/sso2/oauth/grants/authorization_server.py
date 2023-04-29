import time
import uuid
from typing import Any, cast

from authlib.integrations.django_oauth2 import AuthorizationServer, RevocationEndpoint
from authlib.integrations.django_oauth2.authorization_server import (
    create_token_expires_in_generator,
)
from authlib.jose import jwt
from authlib.oauth2 import OAuth2Request
from authlib.oauth2.rfc6749 import ClientCredentialsGrant, ImplicitGrant
from authlib.oauth2.rfc6750 import BearerTokenGenerator
from django.http import HttpRequest, HttpResponse

from sso2.core.models.user_model import User
from sso2.oauth.grants.authorization_code import MyAuthorizationCodeGrant
from sso2.oauth.grants.code_challenge import MyCodeChallenge
from sso2.oauth.grants.introspection_endpoint import MyIntrospectionEndpoint
from sso2.oauth.grants.openid_hybrid import MyOpenIDHybridGrant
from sso2.oauth.grants.openid_implicit import MyOpenIDImplicitGrant
from sso2.oauth.grants.openidcode import MyOpenIDCode
from sso2.oauth.grants.password import MyPasswordGrant
from sso2.oauth.grants.refresh_token import MyRefreshTokenGrant
from sso2.oauth.models.oauth2_client_model import OAuth2Client
from sso2.oauth.models.oauth2_token_model import OAuth2Token


class MyAuthorizationServer(AuthorizationServer):  # type: ignore[misc]
    # This implements most of: https://www.rfc-editor.org/rfc/rfc9068.html
    def access_token_generator(
        self,
        client: OAuth2Client,
        grant_type: str,
        user: User | None = None,
        scope: str | None = None,
    ) -> str:
        tenant = client.tenant
        private_key = tenant.get_private_key()
        now = int(time.time())
        header = {
            "typ": "at+JWT",
            "alg": tenant.algorithm,
            "kid": private_key.thumbprint(),
        }
        payload = {
            # FIXME: reasonable default (issuer) and fetch from 'resource' parameter
            #  to authorize endpoint
            "aud": [client.client_id],
            "auth_time": now,
            "client_id": client.client_id,
            "exp": now + 3600,
            "jti": uuid.uuid4().hex,
            "iat": now,
            "iss": tenant.get_issuer(),
        }
        if user and scope and "openid" in scope:
            payload["sub"] = user.pk
        return str(jwt.encode(header, payload, private_key).decode())

    def refresh_token_generator(
        self,
        client: OAuth2Client,
        grant_type: str,
        user: User | None = None,
        scope: str | None = None,
    ) -> str:
        raise NotImplementedError

    def create_bearer_token_generator(self) -> BearerTokenGenerator:
        """Default method to create BearerToken generator."""
        conf = self.config.get("token_expires_in")
        expires_generator = create_token_expires_in_generator(conf)
        return BearerTokenGenerator(
            access_token_generator=self.access_token_generator,
            refresh_token_generator=self.refresh_token_generator,
            expires_generator=expires_generator,
        )

    def save_token(self, token: dict[str, Any], request: OAuth2Request) -> OAuth2Token:
        """Default method for ``AuthorizationServer.save_token``. Developers MAY
        rewrite this function to meet their own needs.
        """
        client = request.client
        user_id = request.user.pk if request.user else None
        item = self.token_model(client_id=client.client_id, user_id=user_id, **token)
        item.save()
        return cast(OAuth2Token, item)

    def create_authorization_response(
        self,
        request: HttpRequest | None = None,
        grant_user: User | None = None,
    ) -> HttpResponse:
        return cast(
            HttpResponse,
            super().create_authorization_response(request, grant_user),
        )

    def create_endpoint_response(
        self,
        name: str,
        request: HttpRequest | None = None,
    ) -> HttpResponse:
        return cast(HttpResponse, super().create_endpoint_response(name, request))

    def create_token_response(self, request: HttpRequest | None = None) -> HttpResponse:
        return cast(HttpResponse, super().create_token_response(request))


server = MyAuthorizationServer(OAuth2Client, OAuth2Token)
server.register_endpoint(RevocationEndpoint)
server.register_endpoint(MyIntrospectionEndpoint)
server.register_grant(
    MyAuthorizationCodeGrant,
    [
        MyOpenIDCode(),
        MyCodeChallenge(),
    ],
)
server.register_grant(MyPasswordGrant)
server.register_grant(MyRefreshTokenGrant)
server.register_grant(ClientCredentialsGrant)
server.register_grant(ImplicitGrant)
server.register_grant(MyOpenIDImplicitGrant)
server.register_grant(MyOpenIDHybridGrant)
