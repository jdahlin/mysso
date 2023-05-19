from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from sso2.core.models import Tenant, User
from sso2.core.types import HttpRequestWithUser


class PersonalInformationForm(ModelForm[User]):
    ...

    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name", "phone_number"]
        widgets = {
            "first_name": TextInput(attrs={"col-start": 1, "col-end": 2}),
            "last_name": TextInput(attrs={"col-start": 2, "col-end": 3}),
        }

    def clean(self) -> None:
        cleaned_data = super().clean()
        if cleaned_data is None:
            return
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).count() > 0:
            raise ValidationError("Email already exists")


@login_required
@require_http_methods(["GET", "POST"])
def personal_information(request: HttpRequestWithUser, tenant_id: str) -> HttpResponse:
    user = request.user
    tenant = Tenant.get_or_404(tenant_id=tenant_id)
    if request.method == "POST":
        form = PersonalInformationForm(request.POST)
    else:
        form = PersonalInformationForm(instance=user)

    context = {"form": form, "tenant": tenant, "user": user}
    return render(request, "personal_information.html", context)
