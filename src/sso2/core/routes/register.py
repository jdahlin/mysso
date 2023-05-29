from django.core.exceptions import ValidationError
from django.forms import CharField, EmailField, Form, TextInput
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from sso2.core.formfields import PasswordField
from sso2.core.models import User
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
        required=True,
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
    password = PasswordField()
    confirm_password = PasswordField(confirm=True)

    def clean(self) -> None:
        cleaned_data = super().clean()
        if cleaned_data is None:
            return
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).count() > 0:
            raise ValidationError("Email already exists")

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password and password and confirm_password:
            raise ValidationError("password and confirm_password does not match")


@require_http_methods(["GET", "POST"])
def register(
    request: HttpRequestWithUser,
) -> HttpResponse:
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                email=form.cleaned_data["email"],
                username=form.cleaned_data["username"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                password=form.cleaned_data["password"],
                tenant=request.tenant,
            )
            return redirect(reverse("login"))
    else:
        form = SignupForm()

    context = {
        "action": reverse("register"),
        "form": form,
    }
    return render(request, "register.html", context)
