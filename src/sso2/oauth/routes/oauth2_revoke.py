from authlib.integrations.django_oauth2 import RevocationEndpoint
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from sso2.core.types import HttpRequestWithUser
from sso2.oauth.grants.authorization_server import server


@require_http_methods(["POST"])
def oauth2_revoke(request: HttpRequestWithUser) -> HttpResponse:
    return server.create_endpoint_response(RevocationEndpoint.ENDPOINT_NAME, request)
