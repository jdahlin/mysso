"""This module contains public and private Jwk keys."""
import dataclasses
import datetime
import enum
import ipaddress
from functools import lru_cache
from pathlib import Path

from authlib.jose import JsonWebKey, RSAKey
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.types import (
    CertificateIssuerPrivateKeyTypes,
)
from cryptography.x509 import Certificate, Extension, GeneralName
from cryptography.x509.base import _AllowedHashTypes
from django.utils import timezone

key_dir = Path(__file__).parent.parent.parent.parent / "keys"


class JwsAlgorithm(enum.StrEnum):
    EdDSA = "EdDSA"
    ES256 = "ES256"
    ES384 = "ES384"
    ES512 = "ES512"
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    PS256 = "PS256"
    PS384 = "PS384"
    PS512 = "PS512"
    RS256 = "RS256"
    RS384 = "RS384"
    RS512 = "RS512"


@lru_cache
def get_private_key_from_path(path: str) -> RSAKey:
    """Return the private key used to sign JWTs."""
    with (key_dir / path).open() as f:
        private_key = JsonWebKey.import_key(f.read())
        if not private_key.private_key:
            raise AssertionError("Private key is not private")
        return private_key


@lru_cache
def get_public_key_from_path(path: str) -> RSAKey:
    """Return the public key used to verify JWTs."""
    with (key_dir / path).open() as f:
        public_key = JsonWebKey.import_key(f.read())
        if public_key.private_key:
            raise AssertionError("Public key is not public")
        return public_key


@dataclasses.dataclass
class StoredKey:
    key: RSAKey
    path: Path
    private: bool = True

    def write_to_path(self) -> None:
        with self.path.open("wb") as f:
            f.write(self.key.as_pem(is_private=self.private))

        permission = 420 if self.private else 384
        self.path.chmod(permission)


def create_key_pair(
    basename: str,
    algorithm: JwsAlgorithm,
) -> tuple[StoredKey, StoredKey]:
    key_dir.mkdir(exist_ok=True)

    private_key_path = key_dir / (basename + "-private_key.pem")
    generate_new_key = True
    if private_key_path.exists():
        private_jwk = get_private_key_from_path(str(private_key_path))
        generate_new_key = False
    else:
        assert algorithm == "RS256"
        private_jwk = JsonWebKey.generate_key(
            kty="RSA",
            crv_or_size=2048,
            is_private=True,
        )

    private = StoredKey(
        key=private_jwk,
        path=private_key_path,
    )

    public = StoredKey(
        key=private_jwk,
        path=key_dir / (basename + "-public_key.pem"),
        private=False,
    )
    if generate_new_key:
        private.write_to_path()
        public.write_to_path()
    return public, private


# https://www.rfc-editor.org/rfc/rfc8705.html#name-client-registration-metadat
@dataclasses.dataclass
class ClientCertificate:
    """A client certificate."""

    certificate: Certificate
    tls_client_auth_subject_dn: str | None
    tls_client_auth_san_dns: str | None
    tls_client_auth_san_uri: str | None
    tls_client_auth_san_ip: str | None
    tls_client_auth_san_email: str | None


def x509_read_ext_value(san: Extension | None, name: type[GeneralName]) -> str | None:
    if san is None:
        return None
    try:
        return str(san.value.get_values_for_type(name)[0])
    except IndexError:
        return None


def parse_client_certificate(
    x509_certificate: bytes | Certificate,
) -> ClientCertificate:
    if isinstance(x509_certificate, bytes):
        x509_certificate = x509.load_pem_x509_certificate(x509_certificate)
    try:
        x509_extension = x509_certificate.extensions.get_extension_for_class(
            x509.SubjectAlternativeName,
        )
    except x509.ExtensionNotFound:
        x509_extension = None
    return ClientCertificate(
        certificate=x509_certificate,
        tls_client_auth_subject_dn=x509_certificate.subject.rfc4514_string().replace(
            "\\",
            "",
        ),
        tls_client_auth_san_dns=x509_read_ext_value(x509_extension, x509.DNSName),
        tls_client_auth_san_uri=x509_read_ext_value(
            x509_extension,
            x509.UniformResourceIdentifier,
        ),
        tls_client_auth_san_ip=x509_read_ext_value(x509_extension, x509.IPAddress),
        tls_client_auth_san_email=x509_read_ext_value(x509_extension, x509.RFC822Name),
    )


def create_client_certificate(
    issuer_name: str,
    private_key: CertificateIssuerPrivateKeyTypes,
    tls_client_auth_subject_dn: str | None = None,
    tls_client_auth_san_dns: str | None = None,
    tls_client_auth_san_uri: str | None = None,
    tls_client_auth_san_ip: str | None = None,
    tls_client_auth_san_email: str | None = None,
    algorithm: type[_AllowedHashTypes] = hashes.SHA256,
    valid_days: int = 365,
) -> Certificate:
    utcnow = timezone.now()
    builder = x509.CertificateBuilder()
    builder = builder.issuer_name(
        x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, issuer_name)]),
    )
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.not_valid_before(utcnow)
    builder = builder.not_valid_after(utcnow + datetime.timedelta(days=valid_days))
    builder = builder.public_key(private_key.public_key())

    if tls_client_auth_subject_dn:
        builder = builder.subject_name(
            x509.Name.from_rfc4514_string(tls_client_auth_subject_dn),
        )

    extensions = []
    if tls_client_auth_san_dns:
        extensions.append(x509.DNSName(tls_client_auth_san_dns))
    if tls_client_auth_san_uri:
        extensions.append(x509.UniformResourceIdentifier(tls_client_auth_san_uri))
    if tls_client_auth_san_ip:
        extensions.append(x509.IPAddress(ipaddress.ip_address(tls_client_auth_san_ip)))
    if tls_client_auth_san_email:
        extensions.append(x509.RFC822Name(tls_client_auth_san_email))
    if extensions:
        builder = builder.add_extension(
            x509.SubjectAlternativeName(extensions),
            critical=False,
        )
    return builder.sign(
        private_key=private_key,
        algorithm=algorithm(),
    )
