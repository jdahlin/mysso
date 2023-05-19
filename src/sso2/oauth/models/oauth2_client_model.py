from typing import TYPE_CHECKING, Self

from authlib.oauth2.rfc6749 import ClientMixin, list_to_scope, scope_to_list
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    ForeignKey,
    Model,
    TextField,
)
from django.utils.safestring import mark_safe

from sso2.oauth.models.authorized_app_model import OAuth2AuthorizedApp

if TYPE_CHECKING:
    from sso2.core.models import Tenant, User


class OAuth2Client(Model, ClientMixin):  # type: ignore[misc]
    class Meta:
        verbose_name = "OAuth2 Client"
        verbose_name_plural = "OAuth2 Clients"

    tenant = ForeignKey("core.Tenant", on_delete=CASCADE)
    client_name = TextField()
    grant_type = TextField(
        default="",
        choices=[
            ("authorization_code", "Authorization Code"),
            ("client_credentials", "Client Credentials (server to server)"),
            ("urn:ietf:params:oauth:grant-type:device_code", "Device code"),
            ("implicit", "Implicit (legacy)"),
            ("password", "Password (legacy)"),
            ("refresh_token", "Refresh Token"),
        ],
        help_text=mark_safe(
            """
    OAuth2/OpenID Connect grant types. Recommended grant types are:<br>
    <ul>
    <li><a href="https://oauth.net/2/grant-types/authorization-code/">
    authorization_code</a> (optionally with
    <a href="https://oauth.net/2/pkce/">PKCE</a>)</li>
    <li><a href="https://oauth.net/2/grant-types/refresh-token/">
    refresh_token</a></li>
    <li><a href="https://oauth.net/2/grant-types/device-code/">
    device code</a></li>
    <li><a href="https://oauth.net/2/grant-types/client-credentials/">
    client_credentials</a> (for server-to-server communication)</li>
    </ul>

    Legacy, not recommended
    <ul>
    <li><a href="https://oauth.net/2/grant-types/implicit/">implicit</a>
    (not recommended, using access_token in URL)</li>
    <li>password (not recommended, using username and password)</li>
    </ul>

    """,
        ),
    )
    client_id = CharField(max_length=48, unique=True, db_index=True)
    client_secret = CharField(max_length=48, blank=True)
    redirect_uris = TextField(default="", blank=True)
    default_redirect_uri = TextField(blank=True, default="")
    scope = TextField(default="")
    token_endpoint_auth_method = CharField(
        max_length=120,
        default="",
        choices=[
            ("client_secret_basic", "client_secret_basic"),
            ("client_secret_post", "client_secret_post"),
            ("client_secret_jwt", "client_secret_jwt"),
            ("private_key_jwt", "private_key_jwt"),
            # FIXME: authlib doesn't support this yet
        ],
        help_text="""
* client_secret_basic uses the HTTP Basic Authentication Scheme
to authenticate.<br>
<br>
* client_secret_post uses the HTTP POST parameters to authenticate.<br>
<br>
* client_secret_jwt uses the JSON Web Token (JWT) to authenticate.
Compared to client_secret_basic and client_secret_post, client_secret_jwt
doesn`t require sending the actual secret over the network.
This makes it more secure.<br>
<br>
* <a href="https://oauth.net/private-key-jwt/">private_key_jwt</a> uses
the JSON Web Token (JWT) to authenticate. Compared to client_secret_jwt,
private_key_jwt uses a private key to sign the JWT. This makes it more secure.<br>
""",
    )
    response_type = TextField(
        default="",
        help_text="""
Valid options, array of space terminated:<br>
{'code id_token', 'code token', 'code id_token token'} (hybrid)<br>
{'id_token token', 'id_token'} (implicit)<br>
{'code'} (authorization code)<br>
""",
    )
    require_nonce = BooleanField(default=False)
    require_code_challenge = BooleanField(
        default=False,
        verbose_name="Require PKCE",
        help_text=mark_safe(
            """
PKCE (Proof Key for Code Exchange) is a security feature that prevents an attacker
from stealing an authorization code and using it to gain access to a user's account.
See <a href="https://tools.ietf.org/html/rfc7636">RFC 7636</a> for more information.
""",
        ),
    )

    # you can add more fields according to your own need
    # check https://tools.ietf.org/html/rfc7591#section-2

    def __str__(self) -> str:
        return self.client_name

    def get_client_id(self) -> str:
        return self.client_id

    def get_default_redirect_uri(self) -> str:
        return self.default_redirect_uri

    def get_allowed_scope(self, scope: str) -> str:
        if not scope:
            return ""
        allowed = set(scope_to_list(self.scope))
        return str(list_to_scope([s for s in scope.split() if s in allowed]))

    def check_redirect_uri(self, redirect_uri: str) -> bool:
        if redirect_uri == self.default_redirect_uri:
            return True
        return redirect_uri in self.redirect_uris

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
        allowed = self.grant_type.split()
        return grant_type in allowed

    def is_authorized_for(self, user: "User") -> bool:
        return (
            OAuth2AuthorizedApp.objects.filter(
                user=user,
                client=self,
                tenant=self.tenant,
            ).count()
            > 0
        )

    def authorize(self, *, scope: str, user: "User") -> None:
        OAuth2AuthorizedApp.objects.create(
            user=user,
            client=self,
            tenant=self.tenant,
            scope=scope,
        )

    @classmethod
    def create_example(
        cls,
        tenant: "Tenant",
        grant_type: str = "authorization_code",
        response_type: str = "code",
        token_endpoint_auth_method: str = "client_sec" + "ret_basic",
    ) -> Self:
        return cls(
            client_name="test-client",
            client_id="TESTCLIENT",
            client_secret="s3c" + "r3t!",
            redirect_uris="https://example.com/callback",
            response_type=response_type,
            grant_type=grant_type,
            scope="openid email profile",
            tenant=tenant,
            token_endpoint_auth_method=token_endpoint_auth_method,
            require_nonce=False,
        )
