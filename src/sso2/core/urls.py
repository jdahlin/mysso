from django.contrib.auth.views import LogoutView
from django.urls import path

from sso2.core.routes.login_form import NewLoginView
from sso2.core.routes.register import register
from sso2.core.routes.reset_password import reset_password
from sso2.core.routes.twofactor_setup import MFASetupView
from sso2.core.routes.verify_email import verify_email

urlpatterns = [
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
]
