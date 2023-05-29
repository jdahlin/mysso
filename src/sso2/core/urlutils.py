import random
import string

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


SUBDOMAIN_MIN_LENGTH = 3


def generate_subdomain(length: int = 8) -> str:
    if length < SUBDOMAIN_MIN_LENGTH:
        raise ValueError("subdomain must be at least 3 characters long.")
    # 1. First character must be a lowercase letter
    subdomain = random.choice(string.ascii_lowercase)  # noqa: S311
    # 2. Middle is lowercase letter, digit, or hyphen
    subdomain += "".join(
        random.choice(string.ascii_lowercase + string.digits + "-")  # noqa: S311
        for _ in range(length - 2)
    )
    # 3. Last character must be a lowercase letter or digit
    subdomain += random.choice(string.ascii_lowercase + string.digits)  # noqa: S311
    return subdomain
