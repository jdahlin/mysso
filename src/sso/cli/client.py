import secrets

import typer
from rich.console import Console
from rich.table import Table

from sso.cli.helpers import TenantOption, get_db, get_tenant_or_exit
from sso.models import Client, Tenant

app = typer.Typer()
console = Console()


@app.command("create")
def create_client(
    name: str = typer.Option(..., prompt=True),
    secret: str = typer.Option(None, prompt=True, hide_input=True),
    tenant_name: str = TenantOption,
) -> int | None:
    """Add an application to a user."""
    with get_db() as session:
        if secret is None:
            secret = secrets.token_urlsafe(16)
        tenant = get_tenant_or_exit(session, tenant_name)
        if session.query(Client).filter_by(name=name, tenant=tenant).count():
            typer.echo(f"Client: {name!r} already exists.")
            return 2
        client = Client(name=name, secret=secret, tenant=tenant)
        session.add(client)
        session.commit()
    return None


@app.command("delete")
def delete_client(client_name: str, tenant_name: str = TenantOption) -> None:
    """Remove a client from a user."""
    with get_db() as session:
        client = (
            session.query(Client)
            .join(Tenant)
            .filter(Client.name == client_name, Tenant.name == tenant_name)
            .one()
        )
        session.delete(client)
        session.commit()


@app.command("list")
def list_clients(tenant_name: str = TenantOption) -> None:
    table = Table("ID", "Name", "Secret", "Tenant")
    with get_db() as session:
        for client in (
            session.query(Client).join(Tenant).filter(Tenant.name == tenant_name).all()
        ):
            table.add_row(
                client.id,
                client.name,
                client.secret,
                client.tenant.name,
            )
    console.print(table)
