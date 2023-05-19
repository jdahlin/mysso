from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from sso2.oauth.grants.authorization_server import server
from sso2.oauth.grants.introspection_endpoint import MyIntrospectionEndpoint


@require_http_methods(["POST"])
@csrf_exempt
def oauth2_introspect(request: HttpRequest, tenant_id: str) -> HttpResponse:
    return server.create_endpoint_response(
        name=MyIntrospectionEndpoint.ENDPOINT_NAME,
        request=request,
    )
