from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path
from two_factor.urls import urlpatterns as tf_urls

from sso2.core.routes.login_form import NewLoginView
from sso2.core.routes.register import register
from sso2.core.routes.reset_password import reset_password
from sso2.core.routes.twofactor_setup import MFASetupView
from sso2.core.routes.verify_email import verify_email
from sso2.oauth.routes.oauth2_authorize import oauth2_authorize
from sso2.oauth.routes.oauth2_introspect import oauth2_introspect
from sso2.oauth.routes.oauth2_revoke import oauth2_revoke
from sso2.oauth.routes.oauth2_token import oauth2_token
from sso2.oauth.routes.openid_configuration import openid_well_known_configuration
from sso2.oauth.routes.openid_jwks import openid_well_known_jwks
from sso2.portal.routes.home import home

admin.autodiscover()


urlpatterns = [
    path("", include(tf_urls)),
    path("admin/", admin.site.urls),
    path("tenant/<str:tenant_id>/home", home, name="home"),
    path("tenant/<str:tenant_id>/login", NewLoginView.as_view(), name="login"),
    path("tenant/<str:tenant_id>/logout", LogoutView.as_view(), name="logout"),
    path("tenant/<str:tenant_id>/register", register, name="register"),
    path("tenant/<str:tenant_id>/mfa-setup", MFASetupView.as_view(), name="mfa-setup"),
    path(
        "tenant/<str:tenant_id>/verify-email/<str:token>",
        verify_email,
        name="verify_email",
    ),
    path(
        "tenant/<str:tenant_id>/reset-password/<str:token>",
        reset_password,
        name="reset_password",
    ),
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
