import http
from unittest import mock

import httpx
from jwskate import Jwt
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from sso.app import app
from sso.endpoints.hashutils import hash_password
from sso.keys import get_public_key
from sso.models import User


def test_client_credentials(client: TestClient, session: Session) -> None:
    auth = httpx.BasicAuth(
        username="bob@example.com",
        password=hash_password("secret"),
    )
    user = session.query(User).filter_by(email="bob@example.com").one()

    with TestClient(app) as client:
        response = client.post(
            "/oauth2/token",
            auth=auth,
            data={"grant_type": "client_credentials", "scope": "app"},
        )
        assert response.status_code == http.HTTPStatus.OK
        data = response.json()
        access_token = Jwt(data.pop("access_token"))
        assert access_token.claims == {
            "aud": "app",
            "email": "bob@example.com",
            "exp": mock.ANY,
            "iat": mock.ANY,
            "iss": "http://127.0.0.1:5000/",
            "jti": mock.ANY,
            "sub": str(user.id),
        }
        assert access_token.headers == {
            "alg": "ES256",
            "kid": get_public_key().thumbprint(),
        }
        refresh_token = Jwt(data.pop("refresh_token"))
        assert refresh_token.headers == {
            "alg": "ES256",
            "kid": get_public_key().thumbprint(),
        }
        assert refresh_token.claims == {
            "exp": mock.ANY,
            "iat": mock.ANY,
            "iss": "http://127.0.0.1:5000/",
            "jti": mock.ANY,
            "sub": str(user.id),
        }
        assert data == {"expires_in": 60, "token_type": "bearer"}
