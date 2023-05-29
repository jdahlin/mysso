import socket
import uuid

from authlib.jose import RSAKey
from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509 import Certificate
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Model, TextField, UUIDField
from django.http import Http404

from sso2.core.keyutils import (
    JwsAlgorithm,
    create_client_certificate,
    create_key_pair,
    get_private_key_from_path,
    get_public_key_from_path,
)


def get_tenant_issuer(tenant_name: str) -> str:
    return f"https://{tenant_name}.{settings.APP_DOMAIN_NAME}/"


class Tenant(Model):
    id = UUIDField(
        auto_created=True,
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        verbose_name="ID",
    )
    name = TextField(unique=True)
    public_key_path = TextField()
    private_key_path = TextField()
    certificate_pem = TextField()
    algorithm = TextField()
    display_name = TextField()

    @classmethod
    def create_example(
        cls,
        name: str = "demo",
        algorithm: JwsAlgorithm = JwsAlgorithm.RS256,
    ) -> "Tenant":
        public_key, private_key = create_key_pair(basename=name, algorithm=algorithm)
        tenant_issuer_url = get_tenant_issuer(tenant_name=name)
        domain_name = settings.APP_DOMAIN_NAME
        certificate_pem = (
            create_client_certificate(
                issuer_name=tenant_issuer_url,
                private_key=private_key.key.private_key,
                tls_client_auth_san_dns=domain_name,
                tls_client_auth_san_uri=tenant_issuer_url,
                tls_client_auth_san_ip=socket.gethostbyname(domain_name),
                tls_client_auth_san_email=f"admin@{domain_name}",
                tls_client_auth_subject_dn=f"CN={domain_name}",
            )
            .public_bytes(Encoding.PEM)
            .decode("utf-8")
        )

        tenant = Tenant(
            name=name,
            public_key_path=str(public_key.path),
            private_key_path=str(private_key.path),
            certificate_pem=certificate_pem,
            algorithm=algorithm,
        )
        return tenant

    @classmethod
    def get_or_404(cls, *, tenant_id: str) -> "Tenant":
        try:
            return cls.objects.get(pk=tenant_id)
        except (Tenant.DoesNotExist, ValueError, ValidationError):
            try:
                return cls.objects.get(name=tenant_id)
            except Tenant.DoesNotExist as e:
                raise Http404 from e

    def get_issuer(self) -> str:
        return f"https://{self.name}.{settings.APP_DOMAIN_NAME}/"

    def get_private_key(self) -> RSAKey:
        return get_private_key_from_path(self.private_key_path)

    def get_public_key(self) -> RSAKey:
        return get_public_key_from_path(self.public_key_path)

    def get_certificate(self) -> Certificate:
        return x509.load_pem_x509_certificate(self.certificate_pem.encode("utf-8"))

    def __str__(self) -> str:
        return self.name
