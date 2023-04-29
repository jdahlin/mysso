from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from sso2.oauth.grants.authorization_server import server
from sso2.oauth.grants.introspection_endpoint import MyIntrospectionEndpoint


@require_http_methods(["POST"])
def oauth2_introspect() -> HttpResponse:
    return server.create_endpoint_response(MyIntrospectionEndpoint.ENDPOINT_NAME)
