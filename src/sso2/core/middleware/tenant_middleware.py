from collections.abc import Callable

from django.http import HttpRequest, HttpResponse
from rest_framework.response import Response

from sso2.core.models import Tenant
from sso2.core.types import HttpRequestWithUser


class TenantMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequestWithUser) -> HttpResponse:
        tenant_name = request.headers.get("X-Tenant")
        if tenant_name is None:
            tenant_name = request.headers.get("HOST", "").rsplit(".", 2)[0]

        response = Response({"error": "Unauthorized"}, status=401)
        if tenant_name is not None:
            try:
                tenant = Tenant.objects.get(name=tenant_name)
            except Tenant.DoesNotExist:
                pass
            else:
                request.tenant = tenant
                response = self.get_response(request)
                del request.tenant
        return response
