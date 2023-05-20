from django.urls import path

from sso2.portal.routes.home import home
from sso2.portal.routes.personal_information import personal_information
from sso2.portal.routes.security import security

urlpatterns = [
    path("tenant/<uuid:tenant_id>/portal", home, name="home"),
    path(
        "tenant/<uuid:tenant_id>/portal/info",
        personal_information,
        name="personal-information",
    ),
    path("tenant/<uuid:tenant_id>/portal/security", security, name="security"),
]
