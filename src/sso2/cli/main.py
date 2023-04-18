"""Command line interface for the SSO server."""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sso2.django_project.settings")
django.setup()

import typer

from sso2.cli import client, tenant, user  # connection

main_app = typer.Typer(pretty_exceptions_enable=False)
main_app.add_typer(client.app, name="client")
main_app.add_typer(tenant.app, name="tenant")
main_app.add_typer(user.app, name="user")


if __name__ == "__main__":
    main_app()
