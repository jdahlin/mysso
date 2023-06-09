import urllib.parse
from urllib.parse import urljoin

from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from sso2.core.models.tenant_model import Tenant
from sso2.core.types import HttpRequestWithUser
from sso2.oauth.grants.authorization_server import server
from sso2.oauth.models.oauth2_client_model import OAuth2Client


# https://auth0.com/docs/get-started/apis/scopes/openid-connect-scopes
# https://openid.net/specs/openid-connect-core-1_0.html#ScopeClaims
def human_friendly_scope(scope: str) -> str:
    match scope:
        case "openid":
            return "Access your identity"
        case "address":
            return "Access your physical address"
        case "email":
            return "Access your email address"
        case "phone":
            return "Access your phone number"
        case "profile":
            return "Access your profile page, name, gender, birthday and picture"
        case _:
            raise NotImplementedError(scope)


@require_http_methods(["GET", "POST"])
def oauth2_authorize(request: HttpRequestWithUser) -> HttpResponse:
    tenant_name = request.headers["HOST"].rsplit(".", 2)[0]
    tenant = Tenant.get_or_404(tenant_id=tenant_name)
    if not request.user.is_authenticated:
        resolved_login_url = reverse("login")
        url = urllib.parse.urlparse(request.build_absolute_uri())
        next_url = urllib.parse.parse_qs(url.query)["redirect_uri"][0]
        return redirect_to_login(
            next=next_url,
            login_url=urljoin(f"https://{tenant_name}.i-1.app", resolved_login_url),
        )

    grant = server.get_consent_grant(request, end_user=request.user)
    client = grant.client
    grant_user = None
    if client.is_authorized_for(user=request.user):
        grant_user = request.user
    elif request.method == "GET":
        scope = client.get_allowed_scope(grant.request.scope)
        return render(
            request,
            "authorize.html",
            context={
                "grant": grant,
                "client": client,
                "scopes": [human_friendly_scope(s) for s in scope.split()],
                "scope": scope,
                "user": request.user,
            },
        )
    elif request.POST.get("confirm") == "Allow":
        grant_user = request.user
        client = OAuth2Client.objects.get(
            tenant=tenant,
            client_id=request.POST["client_id"],
        )
        client.authorize(scope=request.POST.get("scope"), user=request.user)
    return server.create_authorization_response(request, grant_user=grant_user)
