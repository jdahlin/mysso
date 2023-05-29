import http

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import Encoding
from django.test import Client
from django.urls import reverse

from sso2.core.keyutils import create_client_certificate
from sso2.core.models import Tenant
from sso2.oauth.models import OAuth2Client


@pytest.mark.django_db
def test_application_credential(tenant: Tenant, client: Client) -> None:
    oauth2_client = OAuth2Client.create_example(tenant=tenant)
    oauth2_client.save()

    certificate = create_client_certificate(
        issuer_name=tenant.get_issuer(),
        private_key=tenant.get_private_key().private_key,
        tls_client_auth_subject_dn="CN=test",
    )
    path = reverse(
        "application-credential",
        kwargs={"client_id": str(oauth2_client.id)},
    )
    pem_data = certificate.public_bytes(Encoding.PEM).decode("utf-8")
    response = client.post(
        path,
        data={"pem_data": pem_data, "name": "First key"},
        content_type="application/json",
        HTTP_HOST="test.i-1.app",
    )

    assert response.status_code == http.HTTPStatus.CREATED
    credential = oauth2_client.public_keys.get()
    assert credential.thumbprint == certificate.fingerprint(hashes.SHA1()).hex().upper()
