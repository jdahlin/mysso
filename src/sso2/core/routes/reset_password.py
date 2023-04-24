from authlib.jose.errors import DecodeError
from django.core.exceptions import ValidationError
from django.forms import Form
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from sso2.core.email import verify_email_token
from sso2.core.formfields import PasswordField
from sso2.core.models.tenant_model import Tenant
from sso2.core.types import HttpRequestWithUser


class ResetPasswordForm(Form):
    password = PasswordField()
    confirm_password = PasswordField(confirm=True)

    def clean(self) -> None:
        cleaned_data = super().clean()
        if cleaned_data is None:
            return
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password and password and confirm_password:
            raise ValidationError("password and confirm_password does not match")


# FIXME: replace token with OTP when that is implemented
@require_http_methods(["GET", "POST"])
def reset_password(
    request: HttpRequestWithUser,
    tenant_id: str,
    token: str,
) -> HttpResponse:
    tenant = Tenant.get_or_404(tenant_id=tenant_id)

    form = ResetPasswordForm()
    try:
        user = verify_email_token(tenant=tenant, token=token)
    except (ValueError, DecodeError):
        form.errors["__all__"] = ["The verification link is invalid or has expired."]
    else:
        if request.method == "POST" and user:
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
                user.password = form.cleaned_data["password"]
                user.save()
                return redirect(reverse("login", kwargs={"tenant_id": tenant_id}))

    context = {
        "action": reverse(
            "reset_password",
            kwargs={"tenant_id": tenant_id, "token": token},
        ),
        "form": form,
    }
    return render(request, "reset_password.html", context)
