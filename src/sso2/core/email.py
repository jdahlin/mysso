import time
from typing import TYPE_CHECKING
from urllib.parse import urljoin

from authlib.jose import JWTClaims, jwt
from authlib.jose.errors import InvalidClaimError
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from sso2.core.models.user_model import User
from sso2.django_project.settings.local import FROM_EMAIL

if TYPE_CHECKING:
    from sso2.core.models.tenant_model import Tenant

VERIFY_EMAIL_TEMPLATE = """
Please verify your email address by clicking this link:
<a href="{url}">{url}</a>.
"""


def generate_email_verification_token(user: "User") -> str:
    tenant = user.tenant
    assert tenant is not None
    private_key = tenant.get_private_key()
    header = {"alg": tenant.algorithm, "kid": private_key.thumbprint()}
    now = int(time.time())
    payload = {
        "exp": now + 3600,
        "iat": now,
        "iss": tenant.get_issuer(),
        "sub": str(user.id),
    }
    return str(jwt.encode(header, payload, private_key).decode())


def decode_email_token(*, tenant: "Tenant", token: str) -> JWTClaims:
    public_key = tenant.get_public_key()
    claims = jwt.decode(
        token,
        public_key,
        claims_options={
            "iss": {"essential": True, "values": [tenant.get_issuer()]},
            "exp": {"essential": True},
        },
    )
    try:
        claims.validate()
    except InvalidClaimError as e:
        raise ValueError(str(e)) from e
    return claims


def verify_email_token(*, tenant: "Tenant", token: str) -> "User":
    claims = decode_email_token(tenant=tenant, token=token)
    try:
        user = User.objects.get(pk=claims["sub"])
    except User.DoesNotExist as e:
        raise ValueError("User not found") from e
    else:
        if user.email_verified:
            raise ValueError("Email already verified")
    user.email_verified = True
    user.save()
    return user


def send_verification_email(user: "User") -> tuple[int, str]:
    token = generate_email_verification_token(user)
    assert user.tenant
    url = urljoin(
        settings.APP_HOST,
        reverse(
            "verify_email",
            kwargs={
                "tenant_id": user.tenant.id,
                "token": token,
            },
        ),
    )
    response = send_mail(
        subject="Please verify your email address",
        message="Verify your email",
        html_message=VERIFY_EMAIL_TEMPLATE.format(url=url),
        from_email=FROM_EMAIL,
        recipient_list=[user.email],
    )
    return response, token
