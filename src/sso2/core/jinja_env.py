from typing import Any

from django.conf.urls.static import static
from django.urls import reverse
from django.utils.translation import gettext, ngettext
from jinja2 import Environment, select_autoescape


def environment(**options: Any) -> Environment:
    options["autoescape"] = select_autoescape(  # type: ignore[attr-defined]
        default_for_string=True,
        default=True,
    )
    env = Environment(extensions=["jinja2.ext.i18n"], **options)  # noqa: S701
    env.install_gettext_callables(  # type: ignore[attr-defined]
        gettext=gettext,
        ngettext=ngettext,
        newstyle=True,
    )
    env.globals.update(
        {
            "static": static,
            "url": reverse,
        },
    )
    return env
