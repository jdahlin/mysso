from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from sso2.core.models import Tenant
from sso2.core.types import HttpRequestWithUser


@login_required
@require_http_methods(["GET"])
def security(request: HttpRequestWithUser, tenant_id: str) -> HttpResponse:
    tenant = Tenant.get_or_404(tenant_id=tenant_id)
    context = {"tenant": tenant, "user": request.user}
    return render(request, "security.html", context)
