import dataclasses
import time
from contextlib import nullcontext

import pytest
from django.test import Client
from rest_framework.exceptions import AuthenticationFailed, ParseError

from sso2.core.drfauth import parse_authorization_header
from sso2.core.models import Tenant, User
from sso2.oauth.grants.authorization_server import access_token_generator
from sso2.oauth.models import OAuth2Client


@dataclasses.dataclass
class AuthHeaderData:
    token: str | None = None
    iss: str | None = None
    exp: int | None = dataclasses.field(default_factory=lambda: int(time.time()) + 3600)
    sub: str | None = None

    def get_token(self, oauth2_client: OAuth2Client, user: User) -> str:
        sub = self.sub or user.pk
        token = self.token
        if token is None:
            token = "Bearer " + access_token_generator(
                client=oauth2_client,
                exp=self.exp,
                iss=self.iss,
                sub=sub,
            )
        return token


@pytest.mark.parametrize(
    "auth_header_data,expected_exception",
    [
        pytest.param(
            AuthHeaderData(token="foo bar"),
            ParseError("Invalid authentication header"),
            id="invalid-auth-header",
        ),
        pytest.param(
            AuthHeaderData(token="Bearer invalid-token"),
            ParseError("Invalid token"),
            id="invalid-token",
        ),
        pytest.param(
            AuthHeaderData(iss="https://example.com"),
            AuthenticationFailed('Invalid claim "iss"'),
            id="invalid-claim-iss",
        ),
        pytest.param(
            AuthHeaderData(sub="0"),
            AuthenticationFailed('Invalid claim "sub"'),
            id="invalid-claim-sub",
        ),
        pytest.param(
            AuthHeaderData(exp=-3600),
            AuthenticationFailed("Token expired"),
            id="token-expired",
        ),
        pytest.param(AuthHeaderData(), None, id="ok"),
    ],
)
def test_parse_authorization_header(
    test_client: Client,
    oauth2_client: OAuth2Client,
    tenant: Tenant,
    user: User,
    auth_header_data: AuthHeaderData,
    expected_exception: Exception | None,
) -> None:
    authorization_header = auth_header_data.get_token(
        oauth2_client=oauth2_client,
        user=user,
    )
    if expected_exception:
        ctx = pytest.raises(type(expected_exception), match=str(expected_exception))
    else:
        ctx = nullcontext()
    with ctx:
        parse_result = parse_authorization_header(
            authorization_header=authorization_header,
            tenant=tenant,
        )
        assert parse_result is not None
        assert parse_result.user == user
        assert parse_result.claims.header == {
            "alg": "RS256",
            "typ": "JWT",
            "kid": oauth2_client.tenant.get_public_key().thumbprint(),
        }
        assert parse_result.claims["auth_time"] == pytest.approx(time.time(), abs=2)
        assert parse_result.claims["aud"] == [oauth2_client.client_id]
        assert parse_result.claims["client_id"] == oauth2_client.client_id
        assert parse_result.claims["exp"] == auth_header_data.exp
        assert parse_result.claims["iat"] == pytest.approx(time.time(), abs=2)
        assert parse_result.claims["iss"] == tenant.get_issuer()
        assert parse_result.claims["sub"] == user.pk
        assert isinstance(parse_result.claims["jti"], str)
