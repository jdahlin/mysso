import http
import urllib.parse
from unittest import mock

import pytest
from authlib.jose import jwt
from django.test import Client
from django.urls import reverse

from sso2.core.models import AuthorizationCode, OAuth2Client, Tenant, User


@pytest.mark.django_db
@pytest.mark.parametrize("grant_type", ["authorization_code", "implicit"])
def test_oauth2_authorize(
    client: Client,
    user: User,
    tenant: Tenant,
    grant_type: str,
) -> None:
    assert client.login(email=user.email, password="pass" + "word")
    response_type = "code" if grant_type == "authorization_code" else "token"
    oauth2_client = OAuth2Client.create_example(
        tenant=tenant,
        grant_type=grant_type,
        response_type=response_type,
        token_endpoint_auth_method="none" + "",
    )
    oauth2_client.save()

    path = reverse("oauth2-authorize", kwargs={"tenant_id": tenant.id})
    response = client.post(
        path,
        data={
            "confirm": "Allow",
            "client_id": oauth2_client.client_id,
            "redirect_uri": oauth2_client.redirect_uris,
            "response_type": response_type,
            "scope": "openid email profile",
        },
    )
    assert response.status_code == http.HTTPStatus.FOUND
    if response_type == "code":
        auth_code = AuthorizationCode.objects.get(client_id=oauth2_client.client_id)
        assert auth_code.user == user
        assert auth_code.redirect_uri == oauth2_client.redirect_uris
        assert auth_code.response_type == "code"
        assert auth_code.scope == "openid email profile"
        assert auth_code.nonce is None
        assert auth_code.code_challenge is None
        assert auth_code.code_challenge_method is None

        code = urllib.parse.urlencode({"code": auth_code.code})
        assert response.headers["Location"] == f"https://example.com/callback?{code}"
    else:
        url = urllib.parse.urlparse(response.headers["Location"])
        access_token = urllib.parse.parse_qs(url.fragment)["access_token"][0]
        decoded = jwt.decode(access_token, tenant.get_public_key())
        assert decoded == {
            "aud": None,
            "auth_time": mock.ANY,
            "exp": mock.ANY,
            "iat": mock.ANY,
            "iss": tenant.get_issuer(),
            "client_id": oauth2_client.client_id,
            "sub": user.id,
            "jti": mock.ANY,
        }
        params = {
            "token_type": "Bearer",
            "access_token": access_token,
            "expires_in": 3600,
            "scope": "openid email profile",
        }
        assert response.headers[
            "Location"
        ] == "https://example.com/callback#" + urllib.parse.urlencode(params)
