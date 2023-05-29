import socket

from cryptography.x509 import Certificate
from django.conf import settings

from sso2.core.keyutils import parse_client_certificate
from sso2.core.models import Tenant


def test_tenant(tenant: Tenant) -> None:
    certificate = tenant.get_certificate()
    assert isinstance(certificate, Certificate)
    assert certificate.subject.rfc4514_string() == "CN=" + settings.APP_DOMAIN_NAME
    assert certificate.issuer.rfc4514_string() == "CN=" + tenant.get_issuer()
    assert (
        certificate.public_key().public_numbers()
        == tenant.get_public_key().public_key.public_numbers()
    )
    cc = parse_client_certificate(certificate)
    assert cc.tls_client_auth_san_ip == socket.gethostbyname(settings.APP_DOMAIN_NAME)
    assert cc.tls_client_auth_san_dns == settings.APP_DOMAIN_NAME
    assert cc.tls_client_auth_san_uri == tenant.get_issuer()
    assert cc.tls_client_auth_san_email == f"admin@{settings.APP_DOMAIN_NAME}"
    assert cc.tls_client_auth_subject_dn == f"CN={settings.APP_DOMAIN_NAME}"
