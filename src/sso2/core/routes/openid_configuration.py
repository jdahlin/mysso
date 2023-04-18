from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def openid_well_known_configuration(request: HttpRequest) -> HttpResponse:
    app_host = settings.APP_HOST
    return JsonResponse(
        {
            "issuer": app_host,
            "authorization_endpoint": f"{app_host}{reverse('oauth-authorize')}",
            "token_endpoint": f"{app_host}{reverse('oauth-token')}",
            "token_endpoint_auth_methods_supported": ["client_secret_basic"],
            "token_endpoint_auth_signing_alg_values_supported": [
                "RS512",
                "RS256",
                "ES256",
            ],
            "userinfo_endpoint": f"{app_host}/user/me.json",
            "jwks_uri": f"{app_host}{reverse('jwks')}",
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
                "RS512",
                "RS256",
                "ES256",
                "HS256",
            ],
            "id_token_encryption_alg_values_supported": ["RSA1_5", "A128KW"],
            "id_token_encryption_enc_values_supported": ["A128CBC-HS256", "A128GCM"],
            "request_object_signing_alg_values_supported": ["RS512", "RS256", "ES256"],
            "claims_supported": ["sub", "iss", "auth_time", "acr", "name", "email"],
            "claims_parameter_supported": True,
            "ui_locales_supported": ["en-US"],
        },
    )
