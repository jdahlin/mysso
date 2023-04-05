import typer
from rich import print
from rich.console import Console
from rich.table import Table

from sso.cli.helpers import TenantOption, get_db, get_tenant_or_exit
from sso.exceptions import UnauthorizedError
from sso.keys import get_public_key
from sso.models import Tenant, User
from sso.passwordutils import hash_password
from sso.settings import JWT_ALGORITHM
from sso.tokens import TokenContext

app = typer.Typer()
console = Console()


@app.command()
def create(email: str = typer.Option(..., prompt=True),
           tenant_name: str = TenantOption,
           password: str = typer.Option(..., hide_input=True, prompt=True)) -> None:
    """Add a user to the database."""
    with get_db() as session:
        if session.query(User).filter_by(email=email).count():
            raise SystemExit(f"ERROR: User {email} already exists.")

        tenant_obj = get_tenant_or_exit(session, tenant_name)

        user = User(
            email=email,
            hashed_password=hash_password(password, tenant_obj.password_salt),
            tenant=tenant_obj,
        )
        session.add(user)
        session.commit()

@app.command("list")
def list_tenants(tenant_name: str = TenantOption) -> None:
    users = []
    with get_db() as session:
        for tenant in (session.query(User)
                .join(Tenant)
                .filter(Tenant.name == tenant_name)
                .all()):
            users.append(tenant)

    table = Table("ID", "Email")
    for user in users:
        table.add_row(user.id,
                      user.email,
        )
    console.print(table)

@app.command()
def delete(email: str, tenant_name: str = TenantOption) -> None:
    """Remove a user from the database."""
    with get_db() as session:
        tenant_obj = get_tenant_or_exit(session, tenant_name)
        user = session.query(User).filter_by(email=email, tenant=tenant_obj)

        if not user.exists():
            raise SystemExit(f"User {email} does not exist.")
        session.delete(user)
        session.commit()


@app.command()
def login(
        *,
        email: str = typer.Option(..., prompt=True),
        password: str = typer.Option(..., prompt=True, hide_input=True),
        verify: bool = False,
        tenant_name: str = TenantOption,
) -> int:
    """Login a user and print the access and refresh tokens."""
    with get_db() as session:
        tenant_obj = get_tenant_or_exit(session, tenant_name)
        try:
            user = User.try_password_login(
                email=email,
                password=password,
                tenant=tenant_obj,
            )
        except UnauthorizedError as e:
            print(f"ERROR: {e}")
            return 1
        token_context = TokenContext(user=user)
        access_token, refresh_token = token_context.create_tokens()
        print("[bold]Access token[/bold]")
        print(access_token.headers)
        print(access_token.claims)
        print("[bold]Refresh token[/bold]")
        print(refresh_token.headers)
        print(refresh_token.claims)
        if verify:
            from jwskate import JwsCompact

            jws = JwsCompact(str(access_token))
            print(get_public_key())
            print(jws.verify_signature(get_public_key(), alg=JWT_ALGORITHM))
    return 0
