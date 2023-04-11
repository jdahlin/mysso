import typer
from rich.console import Console
from rich.table import Table

from sso.cli.helpers import get_db
from sso.keys import JwsAlgorithm, key_dir
from sso.models import Tenant

app = typer.Typer()
console = Console()


@app.command("create")
def create_tenant(
    name: str,
    algorithm: JwsAlgorithm = JwsAlgorithm.RS256,
) -> None:
    with get_db() as session:
        if session.query(Tenant).filter_by(name=name).count():
            raise KeyError(f"Tenant: {name} already exists.")
        tenant = Tenant.create_example(
            name=name,
            algorithm=algorithm,
        )
        session.add(tenant)
        session.commit()


@app.command("delete")
def delete_tenant(tenant: str) -> None:
    print(f"Deleting user: {tenant}")


@app.command("list")
def list_tenants() -> None:
    bdirlen = len(str(key_dir))
    tenants = []
    with get_db() as session:
        for tenant in session.query(Tenant).all():
            tenants.append(tenant)

    table = Table("ID", "Name", "Algorithm", "Public Key", "Private Key")
    for tenant in tenants:
        table.add_row(
            tenant.id,
            tenant.name,
            tenant.algorithm,
            tenant.public_key_path[bdirlen:],
            tenant.private_key_path[bdirlen:],
        )
    console.print(table)


if __name__ == "__main__":
    app()
