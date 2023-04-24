from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from sso2.core.email import verify_email_token
from sso2.core.models import Tenant


# FIXME: replace token with OTP when that is implemented
@require_http_methods(["GET"])
def verify_email(request: HttpRequest, tenant_id: str, token: str) -> HttpResponse:
    tenant = Tenant.get_or_404(tenant_id=tenant_id)
    try:
        user = verify_email_token(tenant=tenant, token=token)
    except ValueError:
        messages.error(request, "The verification link is invalid or has expired.")
    else:
        if user.email_verified:
            messages.error(request, "The users email has already been verified.")
        user.email_verified = True
        user.save()
    messages.info(request, "Email verified, you can now login!")
    return redirect(reverse("login", kwargs={"tenant_id": tenant.id}))
