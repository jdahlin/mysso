from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from sso2.core.models.tenant_model import Tenant
from sso2.core.types import HttpRequestWithUser


@require_http_methods(["GET", "POST"])
def login_form(
    request: HttpRequestWithUser,
    tenant_id: str | None = None,
) -> HttpResponse:
    tenant = None
    next_url = request.GET.get("next") or "/"
    if tenant_id is not None:
        tenant = Tenant.get_or_404(tenant_id=tenant_id)
    context = {"next": next_url, "tenant": tenant}
    if request.method == "GET":
        return render(request, "login.html", context)

    email = request.POST.get("username")
    password = request.POST.get("password")
    user = authenticate(request, email=email, password=password, tenant=tenant)
    if user:
        login(request, user)
        next_url = request.POST.get("next") or "/"
        return redirect(next_url)

    context["error"] = "Invalid credentials"
    return render(request, "login.html", context)
