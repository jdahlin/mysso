from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from sso2.core.models import Tenant


@require_http_methods(["GET", "POST"])
def subdomain(request: WSGIRequest) -> HttpResponse:
    tenant_name = Tenant.objects.get(domain=request.environ["HTTP_HOST"])
    return HttpResponse(tenant_name)
