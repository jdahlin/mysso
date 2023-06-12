from urllib.parse import urljoin

from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from sso2.core.types import HttpRequestWithUser


@require_http_methods(["GET"])
def openid_well_known_configuration(
    request: HttpRequestWithUser,
) -> HttpResponse:
    tenant = request.tenant
    issuer = tenant.get_issuer()
    return JsonResponse(
        {
            "issuer": tenant.get_issuer(),
            "authorization_endpoint": urljoin(issuer, reverse("oauth2-authorize")),
            "token_endpoint": urljoin(issuer, reverse("oauth2-token")),
            "userinfo_endpoint": urljoin(issuer, reverse("oauth2-userinfo")),
            "token_endpoint_auth_methods_supported": [
                "client_secret_basic",
                "client_secret_post",
                "none",
                "private_key_jwt",
            ],
            "token_endpoint_auth_signing_alg_values_supported": [
                "RS256",
            ],
            "jwks_uri": urljoin(issuer, reverse("jwks")),
            "response_types_supported": [
                "code",
                "code id_token",
                "id_token",
                "token id_token",
            ],
            "acr_values_supported": [],
            "subject_types_supported": ["public", "pairwise"],
            "userinfo_signing_alg_values_supported": [
                "RS512",
                "RS256",
                "ES256",
                "HS256",
            ],
            "userinfo_encryption_alg_values_supported": ["RSA1_5", "A128KW"],
            "userinfo_encryption_enc_values_supported": ["A128CBC-HS256", "A128GCM"],
            "id_token_signing_alg_values_supported": [
                "RS256",
            ],
            "id_token_encryption_alg_values_supported": ["RSA1_5", "A128KW"],
            "id_token_encryption_enc_values_supported": ["A128CBC-HS256", "A128GCM"],
            "request_object_signing_alg_values_supported": ["RS256"],
            "claims_supported": ["sub", "iss", "auth_time", "acr", "name", "email"],
            "claims_parameter_supported": True,
            "ui_locales_supported": ["en-US"],
        },
    )
