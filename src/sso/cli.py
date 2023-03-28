"""Command line interface for the SSO server."""
import contextlib
from collections.abc import Generator
from typing import Any

import typer

from sso.exceptions import UnauthorizedError
from sso.keys import get_public_key
from sso.models import Application, User
from sso.settings import JWT_ALGORITHM, SQLALCHEMY_DATABASE_URL
from sso.ssotypes import Audience
from sso.tokens import TokenContext

app = typer.Typer()


@contextlib.contextmanager
def get_db() -> Generator[Any, None, None]:
    """Create a database session and yield it."""
    from fastapi_sqlalchemy import DBSessionMiddleware, db

    from sso.app import app as fast_api_app
    DBSessionMiddleware(app=fast_api_app, db_url=SQLALCHEMY_DATABASE_URL)
    with db():
        yield db


@app.command()
def init() -> None:
    """Create database tables and generate keys."""
    from pathlib import Path

    from jwskate import Jwk
    private_jwk = (
        Jwk.generate_for_alg("ES256")
        .with_kid_thumbprint()
        .with_usage_parameters()
    )
    key_dir = Path(__file__).parent.parent / "keys"
    key_dir.mkdir(exist_ok=True)
    private_key_pem = (key_dir / "private_key.pem")
    with private_key_pem.open("wb") as f:
        f.write(private_jwk.to_pem(""))
    private_key_pem.chmod(0o600)
    public_key_pem = (key_dir / "public_key.pem")
    with public_key_pem.open("wb") as f:
        f.write(private_jwk.public_jwk().to_pem(""))
    public_key_pem.chmod(0o644)

    # with get_db() as db:


def ask_password() -> str:
    """Ask the user for a password and return the hashed version."""
    import hashlib
    from getpass import getpass
    password = getpass()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password


@app.command()
def add_user(email: str, hashed_password: str = "") -> None:
    """Add a user to the database."""
    db: Any
    with get_db() as db:
        if db.session.query(User).filter_by(email=email).count():
            raise SystemExit(f"ERROR: User {email} already exists.")
        if not hashed_password:
            hashed_password = ask_password()
        user = User(
            email=email,
            hashed_password=hashed_password,
        )
        db.session.add(user)
        db.session.commit()


@app.command()
def remove_user(email: str) -> None:
    """Remove a user from the database."""
    db: Any
    with get_db() as db:
        user = db.session.query(User).filter_by(email=email)
        if not user.exists():
            raise SystemExit(f"User {email} does not exist.")
        db.session.delete(user)
        db.session.commit()


@app.command()
def add_application(email: str, application: str) -> None:
    """Add an application to a user."""
    db: Any
    with get_db() as db:
        user = db.session.query(User).filter_by(email=email).one()
        user.applications.append(Application(name=application))
        db.session.add(user)
        db.session.commit()


@app.command()
def remove_application(email: str, application: str) -> None:
    """Remove an application from a user."""
    db: Any
    with get_db() as db:
        application = (
            db.session.query(Application)
            .join(User)
            .filter(User.email == email, Application.name == application)
            .one()
        )
        db.session.delete(application)
        db.session.commit()


@app.command()
def login(*,
          email: str, hashed_password: str = "", audience: str = "login",
          verify: bool = False) -> int:
    """Login a user and print the access and refresh tokens."""
    if not hashed_password:
        hashed_password = ask_password()
    with get_db():
        try:
            user = User.try_password_login(
                email=email,
                hashed_password=hashed_password,
                audience=audience,
            )
        except UnauthorizedError as e:
            print(f"ERROR: {e}")
            return 1
        token_context = TokenContext(user=user, audience=Audience(audience))
        access_token, refresh_token = token_context.create_tokens()
        print("Access token")
        print(access_token)
        print(access_token.headers)
        print(access_token.claims)
        print("\nRefresh token")
        print(refresh_token)
        print(refresh_token.headers)
        print(refresh_token.claims)
        if verify:
            from jwskate import JwsCompact
            jws = JwsCompact(str(access_token))
            print(get_public_key())
            print(jws.verify_signature(get_public_key(), alg=JWT_ALGORITHM))
    return 0


if __name__ == "__main__":
    app()
