from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.forms import CharField, EmailField, Form, PasswordInput, TextInput
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from sso2.core.models import User
from sso2.core.models.tenant_model import Tenant
from sso2.core.types import HttpRequestWithUser


class SignupForm(Form):
    email = EmailField(
        widget=TextInput(
            attrs={
                # FIXME: Only autofocus when there is no error
                "autofocus": "1",
                "icon": "fa-inbox",
                "placeholder": "Enter your mail",
            },
        ),
    )
    username = CharField(
        widget=TextInput(
            attrs={"placeholder": "Enter your username", "icon": "fa-user"},
        ),
    )
    first_name = CharField(
        widget=TextInput(
            attrs={
                "placeholder": "Enter your first name, e.g. John",
                "icon": "fa-signature",
            },
        ),
    )
    last_name = CharField(
        widget=TextInput(
            attrs={
                "placeholder": "Enter your last name, e.g. Doe",
                "icon": "fa-thin fa-signature",
            },
        ),
    )
    password = CharField(
        widget=PasswordInput(
            attrs={"placeholder": "Enter your password", "icon": "fa-lock"},
        ),
    )
    confirm_password = CharField(
        widget=PasswordInput(
            attrs={"placeholder": "Confirm your password", "icon": "fa-lock"},
        ),
    )

    def clean(self) -> None:
        cleaned_data = super().clean()
        if cleaned_data is None:
            return
        data = self.cleaned_data["email"]
        if User.objects.filter(email=data).count() > 0:
            raise ValidationError("Email already exists")

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("password and confirm_password does not match")

        if password:
            # Run through all AUTH_PASSWORD_VALIDATORS defined in Django settings
            validate_password(password)


@require_http_methods(["GET", "POST"])
def register(
    request: HttpRequestWithUser,
    tenant_id: str,
) -> HttpResponse:
    tenant = Tenant.get_or_404(tenant_id=tenant_id)
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                email=form.cleaned_data["email"],
                username=form.cleaned_data["username"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                password=form.cleaned_data["password"],
                tenant=tenant,
            )
            return redirect(reverse("login", kwargs={"tenant_id": tenant_id}))
    else:
        form = SignupForm()

    context = {
        "action": reverse("register", kwargs={"tenant_id": tenant_id}),
        "form": form,
    }
    return render(request, "register.html", context)
