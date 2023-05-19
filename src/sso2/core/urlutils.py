from django.db import models
from django.urls import reverse
from django.utils.safestring import SafeString, mark_safe


def build_link(label: str, href: str) -> SafeString:
    return mark_safe(f'<a href="{href}">{label}</a>')


def build_change_url(obj: models.Model, label: str | None = None) -> SafeString:
    if label is None:
        label = str(obj)
    meta = obj._meta  # noqa: SLF001
    href = reverse(f"admin:{meta.app_label}_{meta.model_name}_change", args=[obj.pk])
    return build_link(label=label, href=href)
