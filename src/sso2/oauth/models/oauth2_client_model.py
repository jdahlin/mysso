from typing import TYPE_CHECKING, Self

from authlib.oauth2.rfc6749 import ClientMixin, list_to_scope, scope_to_list
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    Model,
    TextField,
)

from sso2.oauth.models.authorized_app_model import OAuth2AuthorizedApp

if TYPE_CHECKING:
    from sso2.core.models import Tenant, User

AUTH_METHODS = [
    # client_secret_basic uses the HTTP Basic Authentication Scheme
    ("client_secret_basic", "client_secret_basic"),
    # client_secret_post uses the HTTP POST parameters to authenticate.
    ("client_secret_post", "client_secret_post"),
    # client_secret_jwt uses the JSON Web Token (JWT) to authenticate.
    # Compared to client_secret_basic and client_secret_post, client_secret_jwt
    # doesn`t require sending the actual secret over the network.
    ("client_secret_jwt", "client_secret_jwt"),
    # https://oauth.net/private-key-jwt/
    # Uses the JSON Web Token (JWT) to authenticate. Compared to client_secret_jwt,
    # private_key_jwt uses a private key to sign the JWT.
    ("private_key_jwt", "private_key_jwt"),
    # none is used together with PKCE (Proof Key for Code Exchange) to
    # authenticate. PKCE is used to mitigate the threat of having the
    # authorization code intercepted.
    ("none", "none"),
]


class OAuth2Client(Model, ClientMixin):  # type: ignore[misc]
    class Meta:
        verbose_name = "OAuth2 Client"
        verbose_name_plural = "OAuth2 Clients"

    tenant = ForeignKey("core.Tenant", on_delete=CASCADE)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    description = TextField(default="", blank=True)
    # FIXME -> name
    client_name = TextField()

    # FIXME -> DELETE
    client_id = CharField(max_length=48, unique=True, db_index=True)

    # FIXME -> secret
    client_secret = CharField(max_length=48, blank=True)

    # OAuth 2.0 Authorization Code Grant
    # https://oauth.net/2/grant-types/authorization-code/
    authorization_code_grant = BooleanField(default=True)

    # OAuth 2.0 Client Credentials Grant
    # https://oauth.net/2/grant-types/client-credentials
    client_credentials_grant = BooleanField(default=False)

    # OAuth 2.0 Refresh Token Grant
    # https://oauth.net/2/grant-types/refresh-token/
    refresh_token_grant = BooleanField(default=True)

    # OAuth 2.0 Device Code Grant
    # https://oauth.net/2/grant-types/device-code/
    device_code_grant = BooleanField(default=True)

    # OAuth 2.0 Implicit Grant (legacy)
    # https://oauth.net/2/grant-types/implicit
    implicit_grant = BooleanField(default=False)

    # OAuth 2.0 Password Grant (legacy)
    # https://oauth.net/2/grant-types/password/
    password_grant = BooleanField(default=False)

    allowed_callback_uris = TextField(default="", blank=True)

    # FIXME: array of space separated strings
    scope = TextField(default="")

    # Authentication method for the token endpoint.
    token_endpoint_auth_method = CharField(
        max_length=120,
        default="",
        choices=AUTH_METHODS,
    )

    # Valid options, array of space terminated:
    # {'code'} (authorization code)
    response_type = TextField(default="")

    # https://www.rfc-editor.org/rfc/rfc5849#section-3.3
    require_nonce = BooleanField(default=False)

    # PKCE (Proof Key for Code Exchange)
    # https://oauth.net/2/pkce/
    # https://tools.ietf.org/html/rfc7636
    require_code_challenge = BooleanField(
        default=False,
        verbose_name="Require PKCE",
    )

    def __str__(self) -> str:
        return self.client_name

    def get_client_id(self) -> str:
        return self.client_id

    def get_default_redirect_uri(self) -> str | None:
        if self.allowed_callback_uris:
            return self.allowed_callback_uris.split()[0]
        return None

    def get_allowed_scope(self, scope: str) -> str:
        if not scope:
            return ""
        allowed = set(scope_to_list(self.scope))
        return str(list_to_scope([s for s in scope.split() if s in allowed]))

    def check_redirect_uri(self, redirect_uri: str) -> bool:
        return redirect_uri in self.allowed_callback_uris.split()

    def check_client_secret(self, client_secret: str) -> bool:
        return self.client_secret == client_secret

    def check_endpoint_auth_method(self, method: str, endpoint: str) -> bool:
        if endpoint == "token":
            return self.token_endpoint_auth_method == method
        # TODO: developers can update this check method
        return True

    def check_response_type(self, response_type: str) -> bool:
        allowed = self.response_type.split()
        return response_type in allowed

    def check_grant_type(self, grant_type: str) -> bool:
        match grant_type:
            case "authorization_code":
                return self.authorization_code_grant
            case "client_credentials":
                return self.client_credentials_grant
            case "refresh_token":
                return self.refresh_token_grant
            case "device_code":
                return self.device_code_grant
            case "implicit":
                return self.implicit_grant
            case "password":
                return self.password_grant
            case _:
                raise ValueError(f"Unknown grant type: {grant_type}")

    def is_authorized_for(self, user: "User") -> bool:
        return OAuth2AuthorizedApp.objects.filter(
            user=user,
            client=self,
            tenant=self.tenant,
        ).exists()

    def authorize(self, *, scope: str, user: "User") -> None:
        OAuth2AuthorizedApp.objects.create(
            user=user,
            client=self,
            tenant=self.tenant,
            scope=scope,
        )

    def get_access_token(self, *, user: "User | None" = None) -> str:
        from sso2.oauth.grants.authorization_server import access_token_generator

        return access_token_generator(client=self, user=user)

    @classmethod
    def create_example(
        cls,
        tenant: "Tenant",
        grant_type: str = "authorization_code",
        response_type: str = "code",
        token_endpoint_auth_method: str = "client_secret_basic",  # noqa: S107
    ) -> Self:
        kwargs: dict[str, bool] = {}
        if grant_type == "client_credentials":
            kwargs["client_credentials_grant"] = True
        elif grant_type == "authorization_code":
            kwargs["authorization_code_grant"] = True
        elif grant_type == "password":
            kwargs["password_grant"] = True
        elif grant_type == "device_code":
            kwargs["device_code_grant"] = True
        elif grant_type == "refresh_token":
            kwargs["refresh_token_grant"] = True
        elif grant_type == "implicit":
            kwargs["implicit_grant"] = True

        return cls(
            client_name="test-client",
            client_id="TESTCLIENT",
            client_secret="s3c" + "r3t!",
            allowed_callback_uris="https://example.com/callback",
            response_type=response_type,
            scope="openid email profile",
            tenant=tenant,
            token_endpoint_auth_method=token_endpoint_auth_method,
            require_nonce=False,
            **kwargs,
        )


class OAuth2ClientCredential(Model):
    tenant = ForeignKey(
        "core.Tenant",
        on_delete=CASCADE,
    )
    client = ForeignKey(
        OAuth2Client,
        on_delete=CASCADE,
        related_name="public_keys",
    )
    name = TextField()
    pem_data = TextField()
    thumbprint = TextField(default="")
    algorithm = TextField(
        default="RS256",
        choices=[("RS256", "RS256"), ("RS384", "RS384"), ("PS256", "PS256")],
    )
    expires_at = DateTimeField(null=True, blank=True)
