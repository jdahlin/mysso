from base64 import b32encode
from binascii import unhexlify
from typing import Any, cast

from django.contrib.sites.shortcuts import get_current_site
from django.forms import Form
from django.urls import reverse
from formtools.wizard.views import WizardView
from two_factor.utils import get_otpauth_url, totp_digits
from two_factor.views import SetupView

from sso2.core.models import Tenant


class MFASetupView(SetupView):  # type: ignore[misc]
    def get_context_data(self, form: Form, **kwargs: Any) -> dict[str, str]:
        # FIXME: Skips SetupView.get_context_data due to our custom home url
        context = WizardView.get_context_data(self, form, **kwargs)
        if self.steps.current == "generator":
            key = self.get_key("generator")
            rawkey = unhexlify(key.encode("ascii"))
            b32key = b32encode(rawkey).decode("utf-8")
            issuer = get_current_site(self.request).name
            username = self.request.user.get_username()
            otpauth_url = get_otpauth_url(username, b32key, issuer)
            self.request.session[self.session_key_name] = b32key
            context.update(
                {
                    # used in default template
                    "otpauth_url": otpauth_url,
                    "QR_URL": reverse(self.qrcode_url),
                    "secret_key": b32key,
                    # available for custom templates
                    "issuer": issuer,
                    "totp_digits": totp_digits(),
                },
            )
        elif self.steps.current == "validation":
            context["device"] = self.get_device()
        tenant_id = self.request.path.split("/")[2]
        tenant = Tenant.get_or_404(tenant_id=tenant_id)
        context["cancel_url"] = reverse("home", kwargs={"tenant_id": tenant.id})
        return cast(dict[str, str], context)
