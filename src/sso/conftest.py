from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware, db
from sqlalchemy import Connection, create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from starlette.testclient import TestClient

from sso import models
from sso.app import app as fast_api_app
from sso.hashutils import get_password_hasher
from sso.models import Tenant, User
from sso.settings import DB_URL


@pytest.fixture(scope="session")
def connection() -> Iterator[Connection]:
    engine = create_engine(DB_URL)
    connection = engine.connect()
    yield connection
    connection.close()


@pytest.fixture(scope="session")
def setup_database(connection: Connection) -> Iterator[None]:
    models.Base.metadata.drop_all(bind=connection)
    models.Base.metadata.create_all(bind=connection, checkfirst=False)
    DBSessionMiddleware(app=fast_api_app, db_url=connection.engine.url)
    seed_database()
    yield
    models.Base.metadata.drop_all(bind=connection, checkfirst=False)


def seed_database() -> None:
    hasher = get_password_hasher()
    with db() as db1:
        tenant = Tenant.create_example(name="Tenant 1")
        db.session.add(tenant)
        db_user = User(
            email="bob@example.com",
            hashed_password=hasher.hash_password("secret"),
            tenant=tenant,
        )
        db1.session.add(db_user)
        db1.session.commit()


@pytest.fixture
def session(
    setup_database: None,
    connection: Connection,
) -> Iterator[scoped_session[Session]]:
    session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=connection),
    )
    session.begin()
    yield session
    session.rollback()


@pytest.fixture(scope="session")
def app() -> FastAPI:
    return fast_api_app


@pytest.fixture(scope="session")
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture
def tenant(setup_database: None) -> Iterator[Tenant]:
    with db() as db1:
        yield db1.session.query(Tenant).filter_by(name="Tenant 1").one()
