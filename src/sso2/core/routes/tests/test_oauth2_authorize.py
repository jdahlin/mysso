import enum
import http
import urllib.parse
from unittest import mock

import pytest
from authlib.jose import jwt
from django.test import Client
from django.urls import reverse

from sso2.core.models import AuthorizationCode, OAuth2Client, Tenant, User


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


@pytest.mark.django_db
@pytest.mark.parametrize("flow", list(OAuth2Flow))
# Note: remember to keep this in sync with .well-known/openid-configuration
@pytest.mark.parametrize(
    "response_type",
    [
        "code",
        "id_token",
        "token",
        # "code id_token",
        # "token id_token",
    ],
)
def test_oauth2_flows(
    client: Client,
    user: User,
    tenant: Tenant,
    flow: OAuth2Flow,
    response_type: str,
) -> None:
    assert client.login(email=user.email, password="pass" + "word")
    grant_type = flow_to_grant_type(flow)
    oauth2_client = OAuth2Client.create_example(
        tenant=tenant,
        grant_type=grant_type,
        response_type=response_type,
        token_endpoint_auth_method="none" + "",
    )
    oauth2_client.save()

    path = reverse("oauth2-authorize", kwargs={"tenant_id": tenant.id})
    data = {
        "confirm": "Allow",
        "client_id": oauth2_client.client_id,
        "redirect_uri": oauth2_client.redirect_uris,
        "response_type": response_type,
        "nonce": "nonce",
        "scope": "openid email profile",
    }
    if flow == OAuth2Flow.PKCE:
        data["code_challenge"] = "code_challenge"
        data["code_challenge_method"] = "S256"

    response = client.post(path, data=data)
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
                assert auth_code.redirect_uri == oauth2_client.redirect_uris
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
