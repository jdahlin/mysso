from typing import TypedDict, cast

from starlette.responses import Response

from sso.app import app
from sso.settings import JWT_ISSUER


# https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderMetadata
class OpenIDProviderMetadata(TypedDict, total=False):
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    jwks_uri: str
    registration_endpoint: str
    scopes_supported: list[str]
    response_types_supported: list[str]
    response_modes_supported: list[str]
    grant_types_supported: list[str]
    acr_values_supported: list[str]
    subject_types_supported: list[str]
    id_token_signing_alg_values_supported: list[str]
    id_token_encryption_alg_values_supported: list[str]
    id_token_encryption_enc_values_supported: list[str]
    userinfo_signing_alg_values_supported: list[str]
    userinfo_encryption_alg_values_supported: list[str]
    userinfo_encryption_enc_values_supported: list[str]
    request_object_signing_alg_values_supported: list[str]
    request_object_encryption_alg_values_supported: list[str]
    request_object_encryption_enc_values_supported: list[str]
    token_endpoint_auth_methods_supported: list[str]
    token_endpoint_auth_signing_alg_values_supported: list[str]
    display_values_supported: list[str]
    claim_types_supported: list[str]
    claims_supported: list[str]
    service_documentation: str
    claims_locales_supported: list[str]
    ui_locales_supported: list[str]
    claims_parameter_supported: bool
    request_parameter_supported: bool
    request_uri_parameter_supported: bool
    require_request_uri_registration: bool
    op_policy_uri: str
    op_tos_uri: str
    #


@app.get("/.well-known/openid-configuration")
def openid_configuration(response: Response) -> OpenIDProviderMetadata:
    return cast(OpenIDProviderMetadata, {
        "issuer": JWT_ISSUER,
        "authorization_endpoint": f"{JWT_ISSUER}oauth2/authorize",
        "token_endpoint": f"{JWT_ISSUER}oauth2/token",
        "userinfo_endpoint": f"{JWT_ISSUER}oauth2/userinfo",
        "jwks_uri": f"{JWT_ISSUER}.well-known/jwks.json",
        "registration_endpoint": f"{JWT_ISSUER}oauth2/register",
        "response_types_supported": [
            "code",
            "token",
            "id_token",
            "code token",
            "code id_token",
            "token id_token",
            "code token id_token",
            "none",
        ],
        "scopes_supported": [
            "openid",
            "email",
            "profile",
        ],
        "token_endpoint_auth_methods_supported": [
            "client_secret_post",
            "client_secret_basic",
        ],
        "claims_supported": [
            "email",
            "exp",
            "iat"
            "iss",
            # "auth_time",
            # "acr",
            # "name",
            # "given_name",
            # "family_name",
            # "preferred_username",
            "sub",
        ],
        "grant_types_supported": [
            "authorization_code",
            "client_credentials",
            "refresh_token",
        ],
    })
