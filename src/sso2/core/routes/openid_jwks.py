from authlib.jose import KeySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

from sso2.core.keyutils import get_public_key_from_path


@require_http_methods(["GET"])
def openid_well_known_jwks(request: HttpRequest) -> HttpResponse:
    key_set = KeySet(
        [
            get_public_key_from_path("master-public_key.pem"),
        ],
    )
    response = JsonResponse(key_set.as_dict(is_private=False, alg="RSA256", use="sig"))
    response.headers["Cache-Control"] = (
        "public, max_age=3600, " "stale-while-revalidate=3600, " "stale-if-error=3600"
    )
    return response
