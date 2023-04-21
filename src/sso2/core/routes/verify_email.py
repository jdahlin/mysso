from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from sso2.core.email import verify_email_token
from sso2.core.models import Tenant

User = get_user_model()


@csrf_exempt
@require_http_methods(["GET"])
def verify_email(request: HttpRequest, tenant_id: str, token: str) -> HttpResponse:
    tenant = Tenant.get_or_404(tenant_id=tenant_id)
    try:
        verify_email_token(tenant=tenant, token=token)
    except ValueError:
        messages.error(request, "The verification link is invalid or has expired.")
    else:
        messages.info(request, "Email verified, you can now login!")
    return redirect(reverse("login", kwargs={"tenant_id": tenant.id}))
