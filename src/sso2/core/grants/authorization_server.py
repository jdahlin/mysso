from typing import Any, cast

from authlib.integrations.django_oauth2 import AuthorizationServer, RevocationEndpoint
from authlib.oauth2 import OAuth2Request
from authlib.oauth2.rfc6749 import ClientCredentialsGrant, ImplicitGrant
from django.http import HttpRequest, HttpResponse

from sso2.core.grants.authorization_code import MyAuthorizationCodeGrant
from sso2.core.grants.code_challenge import MyCodeChallenge
from sso2.core.grants.introspection_endpoint import MyIntrospectionEndpoint
from sso2.core.grants.openid_hybrid import MyOpenIDHybridGrant
from sso2.core.grants.openid_implicit import MyOpenIDImplicitGrant
from sso2.core.grants.openidcode import MyOpenIDCode
from sso2.core.grants.password import MyPasswordGrant
from sso2.core.grants.refresh_token import MyRefreshTokenGrant
from sso2.core.models.oauth2_client_model import OAuth2Client
from sso2.core.models.oauth2_token_model import OAuth2Token
from sso2.core.models.user_model import User


class MyAuthorizationServer(AuthorizationServer):  # type: ignore[misc]
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
