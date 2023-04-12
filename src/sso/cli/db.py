from typing import cast

import typer
from sqlalchemy import Engine

from sso.cli.helpers import get_db
from sso.cli.tenant import create_tenant
from sso.settings import DB_URL

app = typer.Typer()


@app.command()
def create(*, drop: bool = False) -> None:
    from sso.models.base import Base, load_all_models

    load_all_models()
    with get_db() as session:
        bind = cast(Engine, session.bind)
        if drop:
            Base.metadata.drop_all(bind=bind)
        Base.metadata.create_all(bind=bind)

    try:
        create_tenant(name="master")
    except KeyError:
        typer.echo("Not creating master tenant, as it already exists.")
    else:
        typer.echo("Created master tenant.")


@app.command()
def shell() -> None:
    import subprocess

    subprocess.run(["sqlite3", DB_URL.split("///")[1]])
