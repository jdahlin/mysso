from unittest import mock
from urllib.parse import urljoin

import pytest
from django.conf import settings
from django.urls import reverse
from pytest_django.plugin import _DatabaseBlocker

from sso2.core.email import (
    decode_email_token,
    send_verification_email,
    verify_email_token,
)
from sso2.core.models import User
from sso2.django_project.settings.local import FROM_EMAIL


@pytest.mark.django_db
@mock.patch("sso2.core.email.send_mail")
def test_send_verification_email(
    send_mail: mock.MagicMock,
    user: User,
    django_db_blocker: _DatabaseBlocker,
) -> None:
    tenant = user.tenant
    assert tenant is not None
    with django_db_blocker.unblock():
        assert user.email_verified is False
        _, token = send_verification_email(user)
        verify_email_token(tenant=tenant, token=token)
        user.refresh_from_db()
        assert user.email_verified is True

    claims = decode_email_token(tenant=tenant, token=token)
    assert dict(claims) == {
        "exp": mock.ANY,
        "iat": mock.ANY,
        "iss": tenant.get_issuer(),
        "sub": str(user.id),
    }
    url = urljoin(
        settings.APP_HOST,
        reverse("verify_email", kwargs={"tenant_id": tenant.id, "token": token}),
    )
    assert send_mail.mock_calls == [
        mock.call(
            subject="Please verify your email address",
            message="Verify your email",
            html_message=f"Please verify your email address by "
            f'clicking this link: <a href="{url}"></a>',
            from_email=FROM_EMAIL,
            recipient_list=[user.email],
        ),
    ]
