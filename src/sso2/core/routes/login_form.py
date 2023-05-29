from typing import TYPE_CHECKING

from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.forms import CharField, PasswordInput, TextInput
from django.shortcuts import resolve_url
from django.urls import reverse
from two_factor.forms import AuthenticationTokenForm, BackupTokenForm
from two_factor.views.core import LoginView

if TYPE_CHECKING:
    from sso2.core.types import HttpRequestWithUser


class NewAuthenticationForm(AuthenticationForm):
    request: "HttpRequestWithUser"

    username = CharField(
        widget=TextInput(
            attrs={
                "placeholder": "Enter your username",
                "icon": "fa-user",
                "autofocus": "1",
                "autocomplete": "username",
            },
        ),
    )
    password = CharField(
        widget=PasswordInput(
            attrs={
                "placeholder": "••••••••••••••••",
                "icon": "fa-lock",
                "autocomplete": "current-password",
            },
        ),
    )

    def clean(self) -> dict[str, str]:
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        assert self.request is not None
        if username is not None and password:
            self.user_cache = authenticate(
                request=self.request,
                username=username,
                password=password,
                tenant=self.request.tenant,
            )
            if self.user_cache is None:
                raise ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                    params={"username": self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class NewLoginView(LoginView):  # type: ignore[misc]
    template_name = "login.html"
    form_list = (
        ("auth", NewAuthenticationForm),
        ("token", AuthenticationTokenForm),
        ("backup", BackupTokenForm),
    )

    def get_success_url(self) -> str:
        redirect_to = self.request.GET.get("next", "")
        if not redirect_to:
            return resolve_url(reverse("home"))
        return redirect_to
