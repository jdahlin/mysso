from typing import Any

from django.forms import CharField, PasswordInput, Widget


class PasswordField(CharField):
    widget = PasswordInput

    def __init__(
        self,
        *,
        confirm: bool = False,
        **kwargs: Any,
    ) -> None:
        self.confirm = confirm
        super().__init__(**kwargs)

    def widget_attrs(self, widget: Widget) -> dict[str, Any]:
        attrs = super().widget_attrs(widget)
        attrs["icon"] = "fa-lock"
        placeholder = "Confirm your password" if self.confirm else "Enter your password"
        attrs["placeholder"] = placeholder
        return attrs

    def validate(self, value: str) -> None:
        super().validate(value)
        if self.confirm or not value:
            return
        # Run through all AUTH_PASSWORD_VALIDATORS defined in Django settings
        from django.contrib.auth.password_validation import validate_password

        validate_password(value)
