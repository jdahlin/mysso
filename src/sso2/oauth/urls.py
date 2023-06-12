from django.urls import path

from sso2.oauth.routes.oauth2_authorize import oauth2_authorize
from sso2.oauth.routes.oauth2_introspect import oauth2_introspect
from sso2.oauth.routes.oauth2_revoke import oauth2_revoke
from sso2.oauth.routes.oauth2_token import oauth2_token
from sso2.oauth.routes.oauth2_userinfo import oauth2_userinfo
from sso2.oauth.routes.openid_configuration import openid_well_known_configuration
from sso2.oauth.routes.openid_jwks import openid_well_known_jwks

urlpatterns = [
    path(
        ".well-known/jwks.json",
        openid_well_known_jwks,
        name="jwks",
    ),
    path(
        ".well-known/openid-configuration",
        openid_well_known_configuration,
        name="openid-configuration",
    ),
    path(
        "authorize",
        oauth2_authorize,
        name="oauth2-authorize",
    ),
    path(
        "oauth/introspect",
        oauth2_introspect,
        name="oauth2-introspect",
    ),
    path(
        "oauth/revoke",
        oauth2_revoke,
        name="oauth2-revoke",
    ),
    path(
        "oauth/token",
        oauth2_token,
        name="oauth2-token",
    ),
    path(
        "oauth/userinfo",
        oauth2_userinfo,
        name="oauth2-userinfo",
    ),
]
