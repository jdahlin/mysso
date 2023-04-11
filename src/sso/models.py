"""Models for the SSO service."""
import time
import uuid

from fastapi_sqlalchemy import db
from jwskate import InvalidClaim, Jwk, SignedJwt
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    validates,
)
from starlette import status
from starlette.exceptions import HTTPException

from sso.exceptions import UnauthorizedError
from sso.hashutils import get_password_hasher
from sso.keys import (
    JwsAlgorithm,
    create_key_pair,
    get_private_key_from_path,
    get_public_key_from_path,
)
from sso.settings import JWT_ISSUER

UUIDType = Text(length=36)
hasher = get_password_hasher()


def generate_uuid4() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class Tenant(Base):
    __tablename__ = "tenant"

    id = mapped_column(UUIDType, default=generate_uuid4, primary_key=True)  # noqa: A003

    name = mapped_column(Text, unique=True, index=True)

    clients: Mapped[list["Client"]] = relationship(back_populates="tenant")
    users: Mapped[list["User"]] = relationship(back_populates="tenant")

    public_key_path = mapped_column(Text)
    private_key_path = mapped_column(Text)
    algorithm = mapped_column(Enum(JwsAlgorithm))

    @classmethod
    def create_example(
        cls,
        name: str = "demo",
        algorithm: JwsAlgorithm = JwsAlgorithm.RS256,
    ) -> "Tenant":
        public_key, private_key = create_key_pair(basename=name, algorithm=algorithm)
        tenant = Tenant(
            name=name,
            public_key_path=str(public_key.path),
            private_key_path=str(private_key.path),
            algorithm=algorithm,
        )
        return tenant

    @classmethod
    def get_or_404(cls, *, tenant_id: str) -> "Tenant":
        try:
            return db.session.query(Tenant).filter_by(id=tenant_id).one()
        except NoResultFound as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
            ) from e

    def get_issuer(self) -> str:
        return f"{JWT_ISSUER}tenant/{self.id}"

    def get_private_key(self) -> Jwk:
        return get_private_key_from_path(self.private_key_path)

    def get_public_key(self) -> Jwk:
        return get_public_key_from_path(self.public_key_path)


class Client(Base):
    """A Client that can be logged into."""

    __tablename__ = "client"

    id = mapped_column(UUIDType, default=generate_uuid4, primary_key=True)  # noqa: A003

    name = mapped_column(Text, unique=True, index=True)

    tenant_id = mapped_column(UUIDType, ForeignKey("tenant.id"))

    tenant: Mapped[Tenant] = relationship(back_populates="clients")

    secret = mapped_column(Text)


class User(Base):
    """A user of the system."""

    __tablename__ = "users"

    id = mapped_column(UUIDType, default=generate_uuid4, primary_key=True)  # noqa: A003
    email = mapped_column(Text, unique=True, index=True)
    hashed_password = mapped_column(Text)
    is_active = mapped_column(Boolean, default=True)
    refresh_token_expirations: Mapped[list["PersistentToken"]] = relationship(
        back_populates="user",
    )
    tenant_id = mapped_column(UUIDType, ForeignKey("tenant.id"))
    tenant: Mapped[Tenant] = relationship(back_populates="users")

    @validates("email")
    def validate_email(self, key: str, address: str) -> str:
        if "@" not in address:
            raise ValueError("failed simple email validation")
        return address

    @classmethod
    def try_password_login(
        cls,
        *,
        email: str,
        password: str,
        tenant: Tenant,
    ) -> "User":
        hashed_password = hasher.hash_password(password)
        try:
            user = (
                db.session.query(User)
                .filter_by(
                    email=email,
                    hashed_password=hashed_password,
                    is_active=True,
                    tenant=tenant,
                )
                .one()
            )
        except NoResultFound:
            hasher.dummy_verify()
            raise UnauthorizedError("Invalid credentials") from None
        else:
            return user

    @classmethod
    def try_refresh_token_login(
        cls,
        insecure_token_payload: str,
        tenant: Tenant,
    ) -> "User":
        jwt = SignedJwt(insecure_token_payload)
        try:
            jwt.validate(jwk=tenant.get_public_key(), issuer=tenant.get_issuer())
        except InvalidClaim as e:
            raise UnauthorizedError("Invalid refresh token") from e

        try:
            persistent_token = (
                db.session.query(PersistentToken).filter_by(id=jwt.jwt_token_id).one()
            )
        except NoResultFound:
            raise UnauthorizedError("Invalid refresh token") from None

        if persistent_token.expires_at.timestamp() > time.time():
            raise UnauthorizedError("Refresh token expired")

        user = persistent_token.user
        if not user.is_active:
            raise UnauthorizedError("User is not active")

        db.session.delete(persistent_token)
        db.session.commit()

        return user


class PersistentToken(Base):

    """A persistent token expiration.

    This is used to store refresh tokens and authorization codes.
    """

    __tablename__ = "persistent_token"

    id = mapped_column(UUIDType, default=generate_uuid4, primary_key=True)  # noqa: A003
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship(back_populates="refresh_token_expirations")
    expires_at = mapped_column(DateTime)
