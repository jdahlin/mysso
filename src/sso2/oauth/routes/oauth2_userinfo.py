from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from sso2.core.types import HttpRequestWithUser


@require_http_methods(["GET"])
@csrf_exempt
def oauth2_userinfo(request: HttpRequestWithUser) -> HttpResponse:
    user = request.user
    user_info = {
        "sub": user.id,
        "name": user.username,
        "email": user.email,
        "email_verified": user.email_verified,
    }
    return JsonResponse(user_info)
