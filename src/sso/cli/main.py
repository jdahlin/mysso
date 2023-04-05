"""Command line interface for the SSO server."""

import typer

from sso.cli import client, db, tenant, user

main_app = typer.Typer()
main_app.add_typer(client.app, name="client")
main_app.add_typer(db.app, name="db")
main_app.add_typer(user.app, name="user")
main_app.add_typer(tenant.app, name="tenant")



if __name__ == "__main__":
    main_app()
