import logging
from collections.abc import Callable
from typing import Any

from authlib.jose import JoseError, JWTClaims, jwt
from authlib.oauth2 import OAuth2Request
from authlib.oauth2.rfc6749 import InvalidClientError
from django.urls import reverse

from sso2.core.models import Tenant
from sso2.oauth.models.oauth2_client_model import OAuth2Client, OAuth2ClientCredential

JWT_BEARER_ASSERTION_TYPE = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
log = logging.getLogger(__name__)
ResolveKeyFn = Callable[[dict[str, str], dict[str, str]], str | None]
QueryClientFn = Callable[[str], OAuth2Client | None]


# https://datatracker.ietf.org/doc/html/rfc7523
# https://docs.authlib.org/en/latest/specs/rfc7523.html
class JWTClientAuth:
    """Implementation of Using JWTs for Client Authentication, which is
    defined by RFC7523.
    """

    #: Value of ``client_assertion_type`` of JWTs
    CLIENT_ASSERTION_TYPE = JWT_BEARER_ASSERTION_TYPE

    def __init__(self, *, client_auth_method: str, validate_jti: bool = True) -> None:
        self._validate_jti = validate_jti
        self.client_auth_method = client_auth_method

    def __call__(
        self,
        query_client: QueryClientFn,
        request: OAuth2Request,
    ) -> OAuth2Client | None:
        data = request.form
        assertion_type = data.get("client_assertion_type")
        assertion = data.get("client_assertion")
        if assertion_type == JWT_BEARER_ASSERTION_TYPE and assertion:
            resolve_key = self.create_resolve_key_func(query_client, request)
            self.process_assertion_claims(assertion, resolve_key, request)
            return self.authenticate_client(request.client)
        log.debug("Authenticate via %r failed", self.client_auth_method)

    def create_claims_options(
        self,
        request: OAuth2Request,
    ) -> dict[str, dict[str, Any]]:
        """Create a claims_options for verify JWT payload claims. Developers
        MAY overwrite this method to create a more strict options."""
        # https://tools.ietf.org/html/rfc7523#section-3
        # The Audience SHOULD be the URL of the Authorization Server's Token Endpoint
        tenant_id = request.uri.split("/")[4]
        tenant = Tenant.get_or_404(tenant_id=tenant_id)
        value = reverse("oauth2-token", kwargs={"tenant_id": tenant.id})
        options = {
            "iss": {"essential": True, "validate": _validate_iss},
            "sub": {"essential": True},
            "aud": {"essential": True, "value": value},
            "exp": {"essential": True},
        }
        if self._validate_jti:
            options["jti"] = {"essential": True, "validate": self.validate_jti}
        return options

    def process_assertion_claims(
        self,
        assertion: str,
        resolve_key: ResolveKeyFn,
        request: OAuth2Request,
    ) -> JWTClaims:
        """Extract JWT payload claims from request "assertion", per
        `Section 3.1`_.

        :param assertion: assertion string value in the request
        :param resolve_key: function to resolve the sign key
        :return: JWTClaims
        :raise: InvalidClientError

        .. _`Section 3.1`: https://tools.ietf.org/html/rfc7523#section-3.1
        """
        try:
            claims = jwt.decode(
                assertion,
                resolve_key,
                claims_options=self.create_claims_options(request),
            )
            claims.validate()
        except JoseError as e:
            log.debug("Assertion Error: %r", e)
            raise InvalidClientError from e
        return claims

    def authenticate_client(self, client: OAuth2Client) -> OAuth2Client | None:
        if client.check_endpoint_auth_method(self.client_auth_method, "token"):
            return client
        # Do not raise, as we want to try other methods

    def create_resolve_key_func(
        self,
        query_client: QueryClientFn,
        request: OAuth2Request,
    ) -> ResolveKeyFn:
        def resolve_key(headers: dict[str, str], payload: dict[str, str]) -> str | None:
            # https://tools.ietf.org/html/rfc7523#section-3
            # For client authentication, the subject MUST be the
            # "client_id" of the OAuth client
            client_id = payload["sub"]
            client = query_client(client_id)
            if not client:
                raise InvalidClientError
            request.client = client
            return self.resolve_client_public_key(client, headers)

        return resolve_key

    def validate_jti(self, claims: JWTClaims, jti: str) -> bool:
        # validate_jti is required by OpenID Connect, but it is optional by RFC7523
        # use cache to validate jti value
        # if cache.get(cache_key):
        return True

    def resolve_client_public_key(
        self,
        client: OAuth2Client,
        headers: dict[str, str],
    ) -> str | None:
        if headers["alg"] == "HS256":
            return client.client_secret
        if headers["alg"] == "RS256":
            if "kid" not in headers:
                return None
            public_key = OAuth2ClientCredential.objects.get(
                tenant=client.tenant,
                client=client,
                thumbprint=headers["kid"],
            )
            return public_key.pem_data


def _validate_iss(claims: JWTClaims, iss: str) -> bool:
    return claims["sub"] == iss
