from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from sso2.core.types import HttpRequestWithUser
from sso2.oauth.grants.authorization_server import server


@csrf_exempt
@require_http_methods(["POST"])
def oauth2_token(request: HttpRequestWithUser) -> HttpResponse:
    return server.create_token_response(request)
