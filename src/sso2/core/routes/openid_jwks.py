from authlib.jose import KeySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

from sso2.core.models.tenant_model import Tenant


@require_http_methods(["GET"])
def openid_well_known_jwks(request: HttpRequest, tenant_id: str) -> HttpResponse:
    tenant = Tenant.get_or_404(tenant_id=tenant_id)
    key_set = KeySet([tenant.get_private_key()])
    response = JsonResponse(key_set.as_dict(is_private=False, alg="RSA256", use="sig"))
    response.headers["Cache-Control"] = (
        "public, max_age=3600, " "stale-while-revalidate=3600, " "stale-if-error=3600"
    )
    return response
