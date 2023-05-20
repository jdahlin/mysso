import urllib.parse
import uuid

from authlib.jose import RSAKey
from django.conf import settings
from django.db.models import Model, TextField, UUIDField
from django.http import Http404

from sso2.core.keyutils import (
    JwsAlgorithm,
    create_key_pair,
    get_private_key_from_path,
    get_public_key_from_path,
)


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
    algorithm = TextField()

    @classmethod
    def create_example(
        cls,
        name: str = "demo",
        algorithm: JwsAlgorithm = JwsAlgorithm.RS256,
    ) -> "Tenant":
        public_key, private_key = create_key_pair(basename=name, algorithm=algorithm)
        tenant = Tenant(
            name=name,
            public_key_path=str(public_key.path),
            private_key_path=str(private_key.path),
            algorithm=algorithm,
        )
        return tenant

    @classmethod
    def get_or_404(cls, *, tenant_id: str) -> "Tenant":
        try:
            return cls.objects.get(pk=tenant_id)
        except (Tenant.DoesNotExist, ValueError):
            try:
                return cls.objects.get(name=tenant_id)
            except Tenant.DoesNotExist as e:
                raise Http404 from e

    def get_issuer(self) -> str:
        return urllib.parse.urljoin(settings.APP_HOST, f"tenant/{self.id}")

    def get_private_key(self) -> RSAKey:
        return get_private_key_from_path(self.private_key_path)

    def get_public_key(self) -> RSAKey:
        return get_public_key_from_path(self.public_key_path)

    def __str__(self) -> str:
        return self.name
