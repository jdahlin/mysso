import typer
from rich.console import Console
from rich.table import Table

from sso2.core.keyutils import JwsAlgorithm, key_dir
from sso2.core.models.tenant_model import Tenant

app = typer.Typer()
console = Console()


@app.command("create")
def create_tenant(
    name: str = typer.Option(None, prompt=True),
    algorithm: JwsAlgorithm = JwsAlgorithm.RS256,
) -> None:
    if Tenant.objects.filter(name=name).count():
        raise KeyError(f"Tenant: {name} already exists.")
    tenant = Tenant.create_example(
        name=name,
        algorithm=algorithm,
    )
    tenant.save()


@app.command("delete")
def delete_tenant(tenant: str) -> None:
    print(f"Deleting user: {tenant}")


@app.command("list")
def list_tenants() -> None:
    bdirlen = len(str(key_dir)) + 1
    tenants = []
    for tenant in Tenant.objects.all():
        tenants.append(tenant)

    table = Table("ID", "Name", "Algorithm", "Public Key", "Private Key")
    for tenant in tenants:
        table.add_row(
            str(tenant.id),
            tenant.name,
            tenant.algorithm,
            tenant.public_key_path[bdirlen:],
            tenant.private_key_path[bdirlen:],
        )
    console.print(table)


if __name__ == "__main__":
    app()
