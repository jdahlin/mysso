import http
from unittest import mock

import httpx
from fastapi_sqlalchemy import db
from jwskate import SignedJwt
from starlette.testclient import TestClient

from sso.app import app
from sso.hashutils import get_password_hasher
from sso.models.tenant import Tenant
from sso.models.user import User
from sso.tokens import TokenContext


def test_oauth2_token(client: TestClient, tenant: Tenant) -> None:
    hasher = get_password_hasher()
    auth = httpx.BasicAuth(
        username="bob@example.com",
        password=hasher.hash_password("secret"),
    )
    user = db.session.query(User).filter_by(email="bob@example.com").one()

    authorization_code = TokenContext(tenant=tenant).create_authorization_code(
        user=user,
    )

    with TestClient(app) as client:
        response = client.post(
            f"/tenant/{tenant.id}/oauth2/token",
            auth=auth,
            data={"grant_type": "authorization_code", "code": authorization_code},
        )
        data = response.json()
        assert response.status_code == http.HTTPStatus.OK
        access_token = SignedJwt(data.pop("access_token"))
        assert access_token.claims == {
            "email": "bob@example.com",
            "exp": mock.ANY,
            "iat": mock.ANY,
            "iss": tenant.get_issuer(),
            "jti": mock.ANY,
            "sub": str(user.id),
        }
        assert access_token.headers == {
            "alg": "RS256",
            "kid": tenant.get_public_key().thumbprint(),
        }
        refresh_token = SignedJwt(data.pop("refresh_token"))
        assert refresh_token.headers == {
            "alg": "RS256",
            "kid": tenant.get_public_key().thumbprint(),
        }
        assert refresh_token.claims == {
            "exp": mock.ANY,
            "iat": mock.ANY,
            "iss": tenant.get_issuer(),
            "jti": mock.ANY,
            "sub": str(user.id),
        }
        assert data == {
            "expires_in": 59,
            "token_type": "bearer",
            "userinfo": {"email": "bob@example.com", "id": str(user.id)},
        }
