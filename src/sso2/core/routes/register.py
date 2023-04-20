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
                "placeholder": "Enter your mail",
                "autofocus": "1",
                "icon": "fa-inbox",
            },
        ),
    )
    username = CharField(widget=TextInput(attrs={"placeholder": "Enter your username"}))
    first_name = CharField(
        widget=TextInput(attrs={"placeholder": "Enter your first name, e.g. John"}),
    )
    last_name = CharField(
        widget=TextInput(attrs={"placeholder": "Enter your last name, e.g. Doe"}),
    )
    password = CharField(
        widget=PasswordInput(attrs={"placeholder": "Enter your password"}),
    )
    confirm_password = CharField(
        widget=PasswordInput(attrs={"placeholder": "Confirm your password"}),
    )


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

    context = {"tenant": tenant, "form": form}
    return render(request, "register.html", context)
