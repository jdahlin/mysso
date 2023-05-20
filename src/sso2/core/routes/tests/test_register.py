import http
import secrets
from typing import TypedDict
from unittest import mock
from urllib.parse import urljoin

import pytest
from django.conf import settings
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.test import Client
from django.urls import reverse

from sso2.core.email import generate_email_token
from sso2.core.models import Tenant, User


class EmailFormData(TypedDict):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    confirm_password: str


marker = object()
marker2 = object()


@pytest.mark.django_db
@mock.patch("time.time", mock.MagicMock(return_value=123456789))
@pytest.mark.parametrize(
    "data,status_code,form_errors",
    [
        pytest.param(
            {
                "email": "bob.smith@example.com",
                "username": "bob",
                "first_name": "Bob",
                "last_name": "Smith",
                "password": marker,
                "confirm_password": marker,
            },
            http.HTTPStatus.FOUND,
            {},
            id="ok",
        ),
        pytest.param(
            {
                "email": "",
                "username": "bob",
                "first_name": "Bob",
                "last_name": "Smith",
                "password": marker,
                "confirm_password": marker,
            },
            http.HTTPStatus.OK,
            {"email": ["This field is required."]},
            id="email_required",
        ),
        pytest.param(
            {
                "email": "bob.smith@example.com",
                "username": "",
                "first_name": "Bob",
                "last_name": "Smith",
                "password": marker,
                "confirm_password": marker,
            },
            http.HTTPStatus.OK,
            {"username": ["This field is required."]},
            id="username_required",
        ),
        pytest.param(
            {
                "email": "bob.smith@example.com",
                "username": "bob",
                "first_name": "",
                "last_name": "Smith",
                "password": marker,
                "confirm_password": marker,
            },
            http.HTTPStatus.OK,
            {"first_name": ["This field is required."]},
            id="first_name_required",
        ),
        pytest.param(
            {
                "email": "bob.smith@example.com",
                "username": "bob",
                "first_name": "Bob",
                "last_name": "",
                "password": marker,
                "confirm_password": marker,
            },
            http.HTTPStatus.OK,
            {"last_name": ["This field is required."]},
            id="last_name_required",
        ),
        pytest.param(
            {
                "email": "bob.smith@example.com",
                "username": "bob",
                "first_name": "Bob",
                "last_name": "Smith",
                "password": "",
                "confirm_password": marker,
            },
            http.HTTPStatus.OK,
            {"password": ["This field is required."]},
            id="password_required",
        ),
        pytest.param(
            {
                "email": "bob.smith@example.com",
                "username": "bob",
                "first_name": "Bob",
                "last_name": "Smith",
                "password": marker,
                "confirm_password": "",
            },
            http.HTTPStatus.OK,
            {"confirm_password": ["This field is required."]},
            id="confirm_password_required",
        ),
        pytest.param(
            {
                "email": "bob.smith@example.com",
                "username": "bob",
                "first_name": "Bob",
                "last_name": "Smith",
                "password": marker,
                "confirm_password": marker2,
            },
            http.HTTPStatus.OK,
            {"__all__": ["password and confirm_password does not match"]},
            id="passwords_does_not_match",
        ),
    ],
)
def test_register(
    client: Client,
    tenant: Tenant,
    data: EmailFormData,
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

    response = client.post(
        reverse("register", kwargs={"tenant_id": tenant.id}),
        data=data,
    )
    assert response.status_code == status_code
    if status_code == http.HTTPStatus.OK:
        assert response.context["form"].errors == form_errors
        assert len(mail.outbox) == 0
    else:
        assert response.headers["Location"] == f"/tenant/{tenant.id}/login"

        user = User.objects.get(email="bob.smith@example.com")
        assert user.tenant
        url = urljoin(
            settings.APP_HOST,
            reverse(
                "verify_email",
                kwargs={
                    "tenant_id": user.tenant.id,
                    "token": generate_email_token(user),
                },
            ),
        )

        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert isinstance(email, EmailMultiAlternatives)
        assert email.subject == "Please verify your email address"
        assert email.body == "Verify your email"
        assert email.recipients() == ["bob.smith@example.com"]
        assert email.alternatives == [
            (
                f"\nPlease verify your email address by clicking this link:\n"
                f'<a href="{url}">{url}</a>.\n',
                "text/html",
            ),
        ]
