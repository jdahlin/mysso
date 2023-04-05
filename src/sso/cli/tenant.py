import bcrypt
import typer
from rich.console import Console
from rich.table import Table

from sso.cli.helpers import get_db
from sso.keys import Algorithm, create_key_pair, key_dir
from sso.models import Tenant

app = typer.Typer()
console = Console()


@app.command("create")
def create_tenant(name: str, algorithm: Algorithm = Algorithm.ES256,
                  salt_rounds: int = 12) -> None:
    with get_db() as session:
        if session.query(Tenant).filter_by(name=name).count():
            raise KeyError(f"Tenant: {name} already exists.")
        public_key, private_key = create_key_pair(basename=name, algorithm=algorithm)
        tenant = Tenant(
            name=name,
            public_key_path=str(public_key.path),
            private_key_path=str(private_key.path),
            algorithm=algorithm,
            password_salt=bcrypt.gensalt(salt_rounds),
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

    table = Table("ID", "Name", "Algorithm", "Public Key", "Private Key", "Salt")
    for tenant in tenants:
        table.add_row(tenant.id,
                      tenant.name,
                      tenant.algorithm,
                      tenant.public_key_path[bdirlen:],
                      tenant.private_key_path[bdirlen:],
                      tenant.password_salt.decode(),
        )
    console.print(table)


if __name__ == "__main__":
    app()
