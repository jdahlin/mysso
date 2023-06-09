from typing import TYPE_CHECKING, NamedTuple

from authlib.jose import jwt
from authlib.jose.errors import (
    BadSignatureError,
    DecodeError,
    ExpiredTokenError,
    InvalidClaimError,
)
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.request import Request

from sso2.core.models import User

if TYPE_CHECKING:
    from authlib.jose import JWTClaims

    from sso2.core.models import Tenant


class AuthorizationHeaderParseResult(NamedTuple):
    user: User
    token: str
    claims: "JWTClaims"


# Note: This depends on a tenant so we know which public key to use to decode
def parse_authorization_header(
    *,
    authorization_header: str,
    tenant: "Tenant",
) -> AuthorizationHeaderParseResult:
    if not authorization_header.startswith("Bearer "):
        raise AuthenticationFailed("Invalid authentication header")

    token = authorization_header[len("Bearer ") :]
    try:
        claims = jwt.decode(
            token,
            tenant.get_public_key(),
            claims_options={
                "iss": {"essential": True, "values": [tenant.get_issuer()]},
                "exp": {"essential": True},
            },
        )
    except BadSignatureError as e:
        raise AuthenticationFailed("Invalid token signature") from e
    except DecodeError as e:
        raise AuthenticationFailed("Invalid token") from e

    try:
        claims.validate()
    except InvalidClaimError as e:
        raise AuthenticationFailed(str(e)) from e
    except ExpiredTokenError as e:
        raise AuthenticationFailed("Token expired") from e

    try:
        user = User.objects.get(id=claims["sub"], is_active=True)
    except User.DoesNotExist as e:
        raise AuthenticationFailed('Invalid claim "sub"') from e

    return AuthorizationHeaderParseResult(
        user=user,
        token=token,
        claims=claims,
    )


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request: Request) -> tuple[User, str] | None:
        if True:
            request.user = User.objects.get(username="johannilhad")
            return request.user, "XXX"
        else:
            header = self.authenticate_header(request)
            try:
                value = request.headers[header]
            except KeyError as e:
                raise NotAuthenticated("Authentication header not found") from e

            parse_result = parse_authorization_header(
                authorization_header=value,
                tenant=request.tenant,
            )
            request.claims = parse_result.claims
            request.user = parse_result.user

            return parse_result.user, parse_result.token

    def authenticate_header(self, request: Request) -> str:
        return "Authorization"
