from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from sso2.core.models.tenant_model import Tenant
from sso2.core.types import HttpRequestWithUser


@require_http_methods(["GET", "POST"])
def login_form(request: HttpRequestWithUser) -> HttpResponse:
    if request.method == "GET":
        return render(request, "login.html", {"next": request.GET.get("next")})

    email = request.POST.get("username")
    password = request.POST.get("password")
    tenant = Tenant.objects.first()
    user = authenticate(request, email=email, password=password, tenant=tenant)
    if user:
        login(request, user)

        return redirect(request.POST.get("next") or "/")

    return render(request, "login.html", {"error": "Invalid credentials"})
