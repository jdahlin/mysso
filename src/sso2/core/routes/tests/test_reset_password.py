import http
import secrets
from typing import TypedDict
from unittest import mock

import pytest
from django.test import Client
from django.urls import reverse

from sso2.core.email import generate_email_token
from sso2.core.models import Tenant, User


class RestPasswordForm(TypedDict):
    password: str
    confirm_password: str


marker = object()
marker2 = object()


@pytest.mark.django_db
@mock.patch("time.time", mock.MagicMock(return_value=123456789))
@pytest.mark.parametrize(
    "data,valid_token,status_code,form_errors",
    [
        pytest.param(
            {
                "password": marker,
                "confirm_password": marker,
            },
            True,
            http.HTTPStatus.FOUND,
            {},
            id="ok",
        ),
        pytest.param(
            {
                "password": marker,
                "confirm_password": marker,
            },
            False,
            http.HTTPStatus.OK,
            {"__all__": ["The verification link is invalid or has expired."]},
            id="invalid-token",
        ),
        pytest.param(
            {
                "password": "",
                "confirm_password": marker,
            },
            True,
            http.HTTPStatus.OK,
            {"password": ["This field is required."]},
            id="password_required",
        ),
        pytest.param(
            {
                "password": marker,
                "confirm_password": "",
            },
            True,
            http.HTTPStatus.OK,
            {"confirm_password": ["This field is required."]},
            id="confirm_password_required",
        ),
        pytest.param(
            {
                "password": marker,
                "confirm_password": marker2,
            },
            True,
            http.HTTPStatus.OK,
            {"__all__": ["password and confirm_password does not match"]},
            id="passwords_does_not_match",
        ),
    ],
)
def test_reset_password(
    *,
    test_client: Client,
    tenant: Tenant,
    user: User,
    data: RestPasswordForm,
    valid_token: bool,
    status_code: http.HTTPStatus,
    form_errors: dict[str, list[str]],
) -> None:
    secret = secrets.token_hex(16)
    if data["password"] is marker:
        data["password"] = secret
    if data["confirm_password"] is marker:
        data["confirm_password"] = secret
    if data["confirm_password"] is marker2:
        data["confirm_password"] = secrets.token_hex(16)
    token = generate_email_token(user) if valid_token else "invalid_token"
    response = test_client.post(
        reverse("reset_password", kwargs={"tenant_id": tenant.id, "token": token}),
        data=data,
        HTTP_HOST="test.i-1.app",
    )
    assert response.status_code == status_code
    if status_code == http.HTTPStatus.OK:
        form = response.context.get("form")
        if form:
            assert form.errors == form_errors
    else:
        assert response.headers["Location"] == "/login"
        user.refresh_from_db()
        assert user.password == data["password"]
