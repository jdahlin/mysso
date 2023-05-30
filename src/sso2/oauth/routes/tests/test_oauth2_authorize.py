import base64
import enum
import http
import urllib.parse
from unittest import mock

import pytest
from authlib.jose import JsonWebKey, jwt
from authlib.oauth2.rfc7523 import private_key_jwt_sign
from django.test import Client
from django.urls import reverse

from sso2.core.models import Tenant, User
from sso2.oauth.grants.authentication_methods import JWT_BEARER_ASSERTION_TYPE
from sso2.oauth.models.authorization_code_model import AuthorizationCode
from sso2.oauth.models.oauth2_client_model import OAuth2Client, OAuth2ClientCredential


class OAuth2Flow(enum.StrEnum):
    AUTHORIZATION_CODE = enum.auto()
    IMPLICIT = enum.auto()
    PKCE = enum.auto()


def flow_to_grant_type(flow: OAuth2Flow) -> str:
    match flow:
        case OAuth2Flow.AUTHORIZATION_CODE:
            grant_type = "authorization_code"
        case OAuth2Flow.IMPLICIT:
            grant_type = "implicit"
        case OAuth2Flow.PKCE:
            grant_type = "authorization_code"
        case _:
            raise NotImplementedError(flow)
    return grant_type


def create_client_secret_jwt_assertion(*, oauth2_client: OAuth2Client) -> str:
    client_assertion = private_key_jwt_sign(
        private_key=oauth2_client.client_secret,
        client_id=oauth2_client.client_id,
        token_endpoint=reverse("oauth2-token"),
        alg="HS256",
    )
    return client_assertion.decode("utf-8")


def create_private_key_jwt_assertion(*, oauth2_client: OAuth2Client) -> str:
    tenant = oauth2_client.tenant
    private_jwk = JsonWebKey.generate_key(
        kty="RSA",
        crv_or_size=2048,
        is_private=True,
    )
    kid = private_jwk.thumbprint()
    pem_data = private_jwk.as_pem(is_private=False).decode("utf-8")
    OAuth2ClientCredential(
        tenant=tenant,
        client=oauth2_client,
        pem_data=pem_data,
        thumbprint=kid,
    ).save()
    client_assertion = private_key_jwt_sign(
        private_key=private_jwk.as_pem(is_private=True),
        client_id=oauth2_client.client_id,
        token_endpoint=reverse("oauth2-token"),
        claims=None,
        alg="RS256",
        header={"kid": kid},
    )
    return client_assertion.decode("utf-8")


@pytest.mark.django_db
@pytest.mark.parametrize("flow", list(OAuth2Flow))
@pytest.mark.parametrize(
    "token_endpoint_auth_method",
    [
        "none",
        "client_secret_basic",
        "client_secret_post",
        "client_secret_jwt",
        "private_key_jwt",
        # "self_signed_tls_client_auth",
        # "tls_client_auth",
    ],
)
# Note: remember to keep this in sync with .well-known/openid-configuration
@pytest.mark.parametrize(
    "response_type",
    [
        "code",
        # "id_token",
        # "token",
        # "code id_token",
        # "token id_token",
    ],
)
def test_oauth2_flows(
    test_client: Client,
    user: User,
    tenant: Tenant,
    flow: OAuth2Flow,
    response_type: str,
    token_endpoint_auth_method: str,
) -> None:
    assert test_client.login(email=user.email, password="password")
    grant_type = flow_to_grant_type(flow)
    oauth2_client = OAuth2Client.create_example(
        tenant=tenant,
        grant_type=grant_type,
        response_type=response_type,
        token_endpoint_auth_method=token_endpoint_auth_method,
    )
    oauth2_client.save()

    path = reverse("oauth2-authorize")
    headers = {"HTTP_HOST": "test.i-1.app"}
    data = {
        "confirm": "Allow",
        "client_id": oauth2_client.client_id,
        "redirect_uri": oauth2_client.allowed_callback_uris.split()[0],
        "response_type": response_type,
        "nonce": "nonce",
        "scope": "openid email profile",
    }
    if flow == OAuth2Flow.PKCE:
        data["code_challenge"] = "code_challenge"
        data["code_challenge_method"] = "S256"

    if token_endpoint_auth_method == "client_secret_basic":
        auth = base64.b64encode(
            f"{oauth2_client.client_id}:{oauth2_client.client_secret}".encode("ascii"),
        ).decode("ascii")
        headers["HTTP_AUTHORIZATION"] = f"Basic {auth}"
    elif token_endpoint_auth_method == "client_secret_jwt":
        data["client_assertion"] = create_client_secret_jwt_assertion(
            oauth2_client=oauth2_client,
        )
        data["client_assertion_type"] = JWT_BEARER_ASSERTION_TYPE
    elif token_endpoint_auth_method == "private_key_jwt":
        data["client_assertion"] = create_private_key_jwt_assertion(
            oauth2_client=oauth2_client,
        )
        data["client_assertion_type"] = JWT_BEARER_ASSERTION_TYPE
    response = test_client.post(path, data=data, **headers)
    assert response.status_code == http.HTTPStatus.FOUND

    url = urllib.parse.urlparse(response.headers["Location"])
    form_params = urllib.parse.parse_qs(url.fragment)
    error = form_params.get("error")
    if error:
        raise AssertionError(form_params.get("error_description"))

    for param in response_type.split():
        match param:
            case "code":
                auth_code = AuthorizationCode.objects.get(
                    client_id=oauth2_client.client_id,
                )
                assert auth_code.user == user
                assert (
                    auth_code.redirect_uri
                    == oauth2_client.allowed_callback_uris.split()[0]
                )
                assert auth_code.response_type == "code"
                assert auth_code.scope == "openid email profile"
                assert auth_code.nonce == "nonce"
                if flow == OAuth2Flow.PKCE:
                    assert auth_code.code_challenge == "code_challenge"
                    assert auth_code.code_challenge_method == "S256"
                else:
                    assert auth_code.code_challenge is None
                    assert auth_code.code_challenge_method is None

                code = urllib.parse.urlencode({"code": auth_code.code})
                assert (
                    response.headers["Location"]
                    == f"https://example.com/callback?{code}"
                )
            case "token" | "id_token":
                expected_payload = {
                    "aud": [oauth2_client.client_id],
                    "auth_time": mock.ANY,
                    "exp": mock.ANY,
                    "iat": mock.ANY,
                    "iss": tenant.get_issuer(),
                    "sub": user.id,
                }
                if param == "token":
                    key = "access_token"
                    expected_payload["client_id"] = oauth2_client.client_id
                    expected_payload["jti"] = mock.ANY
                else:
                    key = "id_token"
                    expected_payload["email"] = user.email
                    expected_payload["name"] = user.username
                    expected_payload["nonce"] = "nonce"
                token = form_params[key][0]
                decoded = jwt.decode(token, tenant.get_public_key())
                assert decoded == expected_payload
                if param == "token":
                    params = {
                        "token_type": "Bearer",
                        "access_token": token,
                        "expires_in": 3600,
                        "scope": "openid email profile",
                    }
                else:
                    params = {
                        "expires_in": 3600,
                        "scope": "openid email profile",
                        "id_token": token,
                    }
                assert response.headers[
                    "Location"
                ] == "https://example.com/callback#" + urllib.parse.urlencode(params)
