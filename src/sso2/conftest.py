from collections.abc import Iterator

import pytest
from django.test import Client
from pytest_django.plugin import _DatabaseBlocker

from sso2.core.models import Tenant, User
from sso2.oauth.models.oauth2_client_model import OAuth2Client


@pytest.fixture
def test_client() -> Client:
    return Client()


@pytest.fixture(scope="session")
def tenant(
    django_db_setup: None,
    django_db_blocker: _DatabaseBlocker,
) -> Tenant:
    with django_db_blocker.unblock():
        assert Tenant.objects.count() == 0
        tenant = Tenant.create_example(name="test-tenant")
        tenant.save()
        return tenant


@pytest.fixture(scope="session")
def user(
    django_db_setup: None,
    tenant: Tenant,
    django_db_blocker: _DatabaseBlocker,
) -> Iterator[User]:
    with django_db_blocker.unblock():
        try:
            user = User.objects.get(email="test@example.com")
        except User.DoesNotExist:
            user = User.objects.create_user(
                username="test-user",
                email="test@example.com",
                password="password",
                tenant=tenant,
            )
        else:
            user.tenant = tenant
        user.save()
        yield user


@pytest.fixture
@pytest.mark.django_db
def oauth2_client(tenant: Tenant) -> Iterator[OAuth2Client]:
    oauth2_client = OAuth2Client.create_example(tenant=tenant)
    oauth2_client.save()
    yield oauth2_client
