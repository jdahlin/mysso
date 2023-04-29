from collections.abc import Mapping
from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Field, TextField
from django.forms import TextInput
from django.utils.safestring import SafeString, mark_safe

from sso2.core.models import Tenant
from sso2.core.models.user_model import User

FORM_FIELD_OVERRIDES: Mapping[type[Field[Any, Any]], Mapping[str, Any]] = {
    TextField: {"widget": TextInput(attrs={"size": 100})},
}


class MyUserAdmin(UserAdmin):
    UserAdmin.list_display += ("tenant_link",)  # type: ignore[operator]

    @admin.display(description="Tenant")
    def tenant_link(self, user: User) -> SafeString:
        return mark_safe(
            f'<a href="/admin/core/tenant/{user.tenant_id}/change/">'
            f"{user.tenant.name}"
            f"</a>",
        )


admin.site.register(User, MyUserAdmin)


class TenantCodeAdmin(admin.ModelAdmin[Tenant]):
    formfield_overrides = FORM_FIELD_OVERRIDES
    list_display = [
        "id",
        "name",
        "algorithm",
    ]


admin.site.register(Tenant, TenantCodeAdmin)
