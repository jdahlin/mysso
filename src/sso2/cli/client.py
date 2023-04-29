import secrets
import uuid

import typer
from rich.console import Console
from rich.table import Table

from sso2.cli.helpers import TenantOption, get_tenant_or_exit
from sso2.oauth.models.oauth2_client_model import OAuth2Client

app = typer.Typer()
console = Console()


@app.command("create")
def create_client(
    name: str = typer.Option(..., prompt=True),
    secret: str = typer.Option(None),
    client_id: str = typer.Option(None),
    tenant_name: str = TenantOption,
    scope: str = typer.Option(""),
    response_type: str = typer.Option(""),
    grant_type: str = typer.Option(""),
    token_endpoint_auth_method: str = typer.Option(""),
    redirect_uri: str = typer.Option(""),
) -> int | None:
    """Add an application to a user."""
    if secret is None:
        secret = secrets.token_urlsafe(16)
    if client_id is None:
        client_id = str(uuid.uuid4())
    tenant = get_tenant_or_exit(tenant_name)
    if OAuth2Client.objects.filter(client_name=name, tenant=tenant).count():
        typer.echo(f"Client: {name!r} already exists.")
        return 2
    client = OAuth2Client(
        tenant=tenant,
        client_name=name,
        client_secret=secret,
        client_id=client_id,
        scope=scope,
        response_type=response_type,
        grant_type=grant_type,
        token_endpoint_auth_method=token_endpoint_auth_method,
        redirect_uris=redirect_uri,
        default_redirect_uri=redirect_uri,
    )
    client.save()
    return None


@app.command("delete")
def delete_client(client_name: str, tenant_name: str = TenantOption) -> None:
    """Remove a client from a user."""
    OAuth2Client.objects.filter(
        client_name=client_name,
        tenant__name=tenant_name,
    ).delete()


@app.command("list")
def list_clients(tenant_name: str = TenantOption) -> None:
    table = Table("Name", "Client ID", "Secret", "Grant", "Response", "Method", "Scope")
    for client in OAuth2Client.objects.filter(tenant__name=tenant_name):
        table.add_row(
            client.client_name,
            client.client_id,
            client.client_secret,
            client.grant_type,
            client.response_type,
            client.token_endpoint_auth_method,
            client.scope,
        )
    console.print(table)
