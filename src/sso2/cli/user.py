from unittest.mock import Mock

import typer
from django.contrib.auth import authenticate
from rich import print
from rich.console import Console
from rich.table import Table

from sso2.cli.helpers import TenantOption, get_tenant_or_exit
from sso2.core.models.user_model import User

app = typer.Typer()
console = Console()


@app.command()
def create(
    username: str = typer.Option(..., prompt=True),
    email: str = typer.Option(..., prompt=True),
    tenant_name: str = TenantOption,
    password: str = typer.Option(..., hide_input=True, prompt=True),
) -> None:
    """Add a user to the database."""
    if User.objects.filter(username=username).count():
        raise SystemExit(f"ERROR: User {username} already exists.")

    tenant = get_tenant_or_exit(tenant_name)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        tenant=tenant,
    )
    user.save()


@app.command("list")
def list_users(tenant_name: str = typer.Option(None, "--tenant")) -> None:
    users = []
    q = User.objects.all()
    if tenant_name is not None:
        q = q.filter(tenant__name=tenant_name)
    for user in q:
        users.append(user)

    table = Table("ID", "Email", "Username", "First", "Last", "Flags")
    for user in users:
        flags = ""
        if user.is_staff:
            flags += "S"
        if user.is_superuser:
            flags += "A"
        if user.is_active:
            flags += "X"
        table.add_row(
            str(user.id),
            user.email,
            user.username,
            user.first_name,
            user.last_name,
            flags,
        )
    console.print(table)


@app.command()
def delete(email: str, tenant_name: str = TenantOption) -> None:
    """Remove a user from the database."""
    tenant = get_tenant_or_exit(tenant_name)
    q = User.objects.filter(email=email, tenant=tenant)
    if not q.exists():
        raise SystemExit(f"User {email} does not exist.")
    q.delete()


@app.command()
def login(
    *,
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True),
    verify: bool = False,
    tenant_name: str = TenantOption,
) -> int:
    """Login a user and print the access and refresh tokens."""
    tenant = get_tenant_or_exit(tenant_name)

    request = Mock()
    user = authenticate(request, email=email, password=password, tenant=tenant)
    print(user)
    return 0
