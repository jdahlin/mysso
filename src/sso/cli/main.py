"""Command line interface for the SSO server."""

import typer

from sso.cli import client, connection, db, tenant, user

main_app = typer.Typer()
main_app.add_typer(client.app, name="client")
main_app.add_typer(connection.app, name="connection")
main_app.add_typer(db.app, name="db")
main_app.add_typer(tenant.app, name="tenant")
main_app.add_typer(user.app, name="user")


if __name__ == "__main__":
    main_app()
