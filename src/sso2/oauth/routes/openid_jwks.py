from authlib.jose import KeySet
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

from sso2.core.keyutils import JwsAlgorithm
from sso2.core.types import HttpRequestWithUser


@require_http_methods(["GET"])
def openid_well_known_jwks(request: HttpRequestWithUser) -> HttpResponse:
    key_set = KeySet([request.tenant.get_private_key()])
    data = key_set.as_dict(is_private=False, alg=JwsAlgorithm.RS256, use="sig")
    response = JsonResponse(data)
    response.headers[
        "Cache-Control"
    ] = "public, max_age=3600, stale-while-revalidate=3600, stale-if-error=3600"
    return response
