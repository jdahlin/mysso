from django.contrib import admin
from django.urls import path

from sso2.core.routes.login_form import login_form
from sso2.core.routes.oauth2_authorize import oauth2_authorize
from sso2.core.routes.oauth2_introspect import oauth2_introspect
from sso2.core.routes.oauth2_revoke import oauth2_revoke
from sso2.core.routes.oauth2_token import oauth2_token
from sso2.core.routes.openid_configuration import openid_well_known_configuration
from sso2.core.routes.openid_jwks import openid_well_known_jwks

admin.autodiscover()
admin.site.login = login_form  # type: ignore[assignment]


urlpatterns = [
    path("admin/", admin.site.urls),
    path("tenant/<str:tenant_id>/login", login_form, name="login"),
    path(
        "tenant/<str:tenant_id>/protocol/oauth2/authorize",
        oauth2_authorize,
        name="oauth2-authorize",
    ),
    path(
        "tenant/<str:tenant_id>/protocol/oauth2/introspect",
        oauth2_introspect,
        name="oauth2-introspect",
    ),
    path(
        "tenant/<str:tenant_id>/protocol/oauth2/revoke",
        oauth2_revoke,
        name="oauth2-revoke",
    ),
    path(
        "tenant/<str:tenant_id>/protocol/oauth2/token",
        oauth2_token,
        name="oauth2-token",
    ),
    path(
        "tenant/<str:tenant_id>/.well-known/jwks.json",
        openid_well_known_jwks,
        name="jwks",
    ),
    path(
        "tenant/<str:tenant_id>/.well-known/openid-configuration",
        openid_well_known_configuration,
        name="openid-configuration",
    ),
]
