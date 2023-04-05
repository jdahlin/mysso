import bcrypt
import typer

from sso.cli.helpers import get_db
from sso.cli.tenant import create_tenant

app = typer.Typer()

@app.command()
def create(*, drop: bool = False) -> None:
    from sso.models import Base
    with get_db() as session:
        if drop:
            Base.metadata.drop_all(bind=session.bind)
        Base.metadata.create_all(bind=session.bind)

    salt = bcrypt.gensalt(rounds=12)
    print(salt)
    try:
        create_tenant(name="master")
    except KeyError:
        typer.echo("Not creating master tenant, as it already exists.")
    else:
        typer.echo("Created master tenant.")
