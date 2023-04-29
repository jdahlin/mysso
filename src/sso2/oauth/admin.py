import secrets
from uuid import uuid4

from django.contrib import admin
from django.http import HttpRequest
from django.utils.safestring import SafeString, mark_safe

from sso2.core.admin import FORM_FIELD_OVERRIDES
from sso2.oauth.models.authorization_code_model import AuthorizationCode
from sso2.oauth.models.oauth2_client_model import OAuth2Client
from sso2.oauth.models.oauth2_token_model import OAuth2Token


# Register your models here.
class OAuth2ClientAdmin(admin.ModelAdmin[OAuth2Client]):
    list_display = ["client_link", "tenant_link"]
    formfield_overrides = FORM_FIELD_OVERRIDES

    @admin.display(description="Client")
    def client_link(self, client: OAuth2Client) -> SafeString:
        return mark_safe(
            f'<a href="/admin/core/oauth2client/{client.id}/change/">'
            f"{client.client_name} (#{client.id})"
            f"</a>",
        )

    @admin.display(description="Tenant")
    def tenant_link(self, client: OAuth2Client) -> SafeString:
        return mark_safe(
            f'<a href="/admin/core/tenant/{client.tenant_id}/change/">'
            f"{client.tenant.name}"
            f"</a>",
        )

    def get_changeform_initial_data(
        self,
        request: HttpRequest,
    ) -> dict[str, str | list[str]]:
        return {
            "client_id": str(uuid4()),
            "client_secret": secrets.token_urlsafe(24),
            "response_type": "code",
            "scope": "openid email profile",
        }


admin.site.register(OAuth2Client, OAuth2ClientAdmin)


class OAuth2TokenAdmin(admin.ModelAdmin[OAuth2Token]):
    formfield_overrides = FORM_FIELD_OVERRIDES
    list_display = [
        "token",
        "client",
        "scope",
        "user",
        "issued_at",
        "expires_in",
        "revoked",
    ]

    @admin.display()
    def token(self, token: OAuth2Token) -> SafeString:
        return mark_safe(
            f"OAuth2 Token "
            f'<a href="/admin/core/oauth2token/{token.id}/change/">'
            f"#{token.id}"
            f"</a>",
        )

    @admin.display()
    def client(self, token: OAuth2Token) -> SafeString:
        client = OAuth2Client.objects.get(client_id=token.client_id)
        return mark_safe(
            f'<a href="/admin/core/oauth2client/{client.id}/change/">'
            f"{client.client_name}"
            f"</a>",
        )


admin.site.register(OAuth2Token, OAuth2TokenAdmin)


class AuthorizationCodeAdmin(admin.ModelAdmin[AuthorizationCode]):
    formfield_overrides = FORM_FIELD_OVERRIDES
    list_display = [
        "auth_code",
        "client",
        "user",
        "scope",
        "response_type",
        "auth_time",
        "expired",
    ]

    @admin.display()
    def auth_code(self, code: AuthorizationCode) -> SafeString:
        return mark_safe(
            f'<a href="/admin/core/oauth2code/{code.id}/change/">'
            f"Auth Code (#{code.id})"
            f"</a>",
        )

    @admin.display()
    def client(self, code: AuthorizationCode) -> SafeString:
        client = OAuth2Client.objects.get(client_id=code.client_id)
        return mark_safe(
            f'<a href="/admin/core/oauth2client/{client.id}/change/">'
            f"{client.client_name}"
            f"</a>",
        )

    @admin.display()
    def expired(self, code: AuthorizationCode) -> bool:
        return code.is_expired()


admin.site.register(AuthorizationCode, AuthorizationCodeAdmin)
