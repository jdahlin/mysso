import typer
from rich.console import Console
from rich.table import Table

from sso.cli.helpers import TenantOption, get_db, get_tenant_or_exit
from sso.models.auth_connection import AuthConnection
from sso.models.tenant import Tenant

app = typer.Typer()
console = Console()


@app.command("create")
def create_connection(
    tenant_name: str = TenantOption,
    name: str = typer.Option(..., prompt=True),
    issuer_url: str = typer.Option(None, prompt=True),
    client_id: str = typer.Option(None, prompt=True),
    secret: str = typer.Option(None, prompt=True, hide_input=True),
) -> int | None:
    """Add an auth connection."""
    with get_db() as session:
        tenant = get_tenant_or_exit(session, tenant_name)
        if session.query(AuthConnection).filter_by(name=name, tenant=tenant).count():
            typer.echo(f"Connection: {name!r} already exists.")
            return 2
        auth_conn = AuthConnection(
            name=name,
            issuer_url=issuer_url,
            client_id=client_id,
            tenant=tenant,
            client_secret=secret,
        )
        session.add(auth_conn)
        session.commit()
    return None


@app.command("list")
def list_connections(tenant_name: str = TenantOption) -> None:
    table = Table("ID", "Name", "Issuer", "Client ID")
    with get_db() as session:
        for auth_conn in (
            session.query(AuthConnection)
            .join(Tenant)
            .filter(Tenant.name == tenant_name)
            .all()
        ):
            table.add_row(
                auth_conn.id,
                auth_conn.name,
                auth_conn.issuer_url,
                auth_conn.client_id,
            )
    console.print(table)
