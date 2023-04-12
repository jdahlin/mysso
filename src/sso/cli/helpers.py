import contextlib
from collections.abc import Generator

import typer
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from sso.models.tenant import Tenant
from sso.settings import SQLALCHEMY_DATABASE_URL


@contextlib.contextmanager
def get_db() -> Generator[Session, None, None]:
    """Create a database session and yield it."""
    from fastapi_sqlalchemy import DBSessionMiddleware, db

    from sso.app import app as fast_api_app

    DBSessionMiddleware(app=fast_api_app, db_url=SQLALCHEMY_DATABASE_URL)
    with db() as db1:
        yield db1.session


def get_tenant_or_exit(session: Session, tenant: str) -> Tenant:
    try:
        return session.query(Tenant).filter_by(name=tenant).one()
    except NoResultFound:
        typer.echo(f"No such tenant: {tenant}")
        raise typer.Exit(1) from None


TenantOption = typer.Option("master", "--tenant")
