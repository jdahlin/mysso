import pytest
from cryptography.hazmat.primitives.serialization import Encoding

from sso2.core.keyutils import create_client_certificate, parse_client_certificate
from sso2.core.models import Tenant


@pytest.mark.parametrize(
    "tls_client_auth_subject_dn",
    [
        "CN=common",
        "CN=common,L=locality,ST=state,O=org,OU=unit,C=SE,STREET=street,DC=domain,UID=user_id",
    ],
    ids=["common", "full"],
)
@pytest.mark.parametrize(
    "tls_client_auth_san_dns",
    ["san-dns.example.com", None],
    ids=["dns", ""],
)
@pytest.mark.parametrize("tls_client_auth_san_ip", ["1.2.3.4", None], ids=["ip", ""])
@pytest.mark.parametrize(
    "tls_client_auth_san_uri",
    ["https://san-uri.example.com", None],
    ids=["uri", ""],
)
@pytest.mark.parametrize(
    "tls_client_auth_san_email",
    ["san-email@example.com", None],
    ids=["email", ""],
)
def test_create_client_certificate(
    tenant: Tenant,
    tls_client_auth_subject_dn: str | None,
    tls_client_auth_san_dns: str | None,
    tls_client_auth_san_ip: str | None,
    tls_client_auth_san_uri: str | None,
    tls_client_auth_san_email: str | None,
) -> None:
    certificate = create_client_certificate(
        issuer_name=tenant.get_issuer(),
        private_key=tenant.get_private_key().private_key,
        tls_client_auth_subject_dn=tls_client_auth_subject_dn,
        tls_client_auth_san_dns=tls_client_auth_san_dns,
        tls_client_auth_san_ip=tls_client_auth_san_ip,
        tls_client_auth_san_uri=tls_client_auth_san_uri,
        tls_client_auth_san_email=tls_client_auth_san_email,
    )
    client_certificate = parse_client_certificate(
        certificate.public_bytes(Encoding.PEM),
    )
    assert (
        client_certificate.certificate.issuer.rfc4514_string()
        == "CN=" + tenant.get_issuer()
    )
    assert client_certificate.tls_client_auth_subject_dn == tls_client_auth_subject_dn
    assert client_certificate.tls_client_auth_san_dns == tls_client_auth_san_dns
    assert client_certificate.tls_client_auth_san_ip == tls_client_auth_san_ip
    assert client_certificate.tls_client_auth_san_uri == tls_client_auth_san_uri
    assert client_certificate.tls_client_auth_san_email == tls_client_auth_san_email
