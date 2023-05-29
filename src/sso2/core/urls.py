from django.contrib.auth.views import LogoutView
from django.urls import path

from sso2.core.api.application import ApplicationViewSet
from sso2.core.api.tenant import TenantViewSet
from sso2.core.pathrouter import PathRouter
from sso2.core.routes.login_form import NewLoginView
from sso2.core.routes.register import register
from sso2.core.routes.reset_password import reset_password
from sso2.core.routes.subdomain import subdomain
from sso2.core.routes.twofactor_setup import MFASetupView
from sso2.core.routes.verify_email import verify_email

router = PathRouter(trailing_slash=False)
router.register("application", ApplicationViewSet, basename="application")
router.register("tenant", TenantViewSet, basename="tenant")
urlpatterns = router.urls

urlpatterns += [
    # Auth0 compatible endpoints
    path("login", NewLoginView.as_view(), name="login"),
    path("v2/logout", LogoutView.as_view(), name="logout"),
    path("tenant/<uuid:tenant_id>/logout", LogoutView.as_view(), name="logout"),
    path("register", register, name="register"),
    path("tenant/<uuid:tenant_id>/mfa-setup", MFASetupView.as_view(), name="mfa-setup"),
    path(
        "tenant/<uuid:tenant_id>/verify-email/<str:token>",
        verify_email,
        name="verify_email",
    ),
    path(
        "tenant/<uuid:tenant_id>/reset-password/<str:token>",
        reset_password,
        name="reset_password",
    ),
    path(
        "subdomain",
        subdomain,
        name="subdomain",
    ),
]
