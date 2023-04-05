"""Models for the SSO service."""
import json
import time
import uuid

from fastapi_sqlalchemy import db
from jwskate import JwsCompact
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship, validates

from sso.exceptions import UnauthorizedError
from sso.keys import Algorithm, get_public_key
from sso.passwordutils import hash_password

UUIDType = Text(length=36)


def generate_uuid4() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class Tenant(Base):
    __tablename__ = "tenant"

    id = Column(UUIDType, default=generate_uuid4, primary_key=True)  # noqa: A003

    name = Column(Text, unique=True, index=True)

    clients: Mapped[list["Client"]] = relationship(back_populates="tenant")
    users: Mapped[list["User"]] = relationship(back_populates="tenant")

    public_key_path = Column(Text)
    private_key_path = Column(Text)
    algorithm = Column(Enum(Algorithm))
    password_salt = Column(Text)


class Client(Base):
    """A Client that can be logged into."""

    __tablename__ = "client"

    id = Column(UUIDType, default=generate_uuid4, primary_key=True)  # noqa: A003

    name = Column(Text, unique=True, index=True)

    tenant_id = Column(UUIDType, ForeignKey("tenant.id"))

    tenant: Mapped[Tenant] = relationship(back_populates="clients")

    secret = Column(Text)


class User(Base):
    """A user of the system."""

    __tablename__ = "users"

    id = Column(UUIDType, default=generate_uuid4, primary_key=True)  # noqa: A003
    email = Column(Text, unique=True, index=True)
    hashed_password = Column(Text)
    is_active = Column(Boolean, default=True)
    refresh_token_expirations: Mapped[list["RefreshTokenExpiration"]] = relationship(
        back_populates="user",
    )
    tenant_id = Column(UUIDType, ForeignKey("tenant.id"))
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
        hashed_password = hash_password(password, tenant.password_salt)
        try:
            user = (
                db.session.query(User)
                .filter_by(email=email, hashed_password=hashed_password, is_active=True)
                .one()
            )
        except NoResultFound:
            raise UnauthorizedError("Invalid credentials") from None
        else:
            return user

    @classmethod
    def try_refresh_token_login(
            cls,
            insecure_token_payload: str,
            audience: str,
    ) -> "User":
        jws = JwsCompact(insecure_token_payload)
        if not jws.verify_signature(get_public_key()):
            raise UnauthorizedError("Invalid refresh token")

        payload = json.loads(jws.payload)
        try:
            refresh_token_expiration = (
                db.session.query(RefreshTokenExpiration)
                .filter_by(id=payload["jti"])
                .one()
            )
        except NoResultFound:
            raise UnauthorizedError("Invalid refresh token") from None

        if refresh_token_expiration.expires_at.timestamp() > time.time():
            raise UnauthorizedError("Refresh token expired")

        user = refresh_token_expiration.user
        db.session.delete(refresh_token_expiration)
        db.session.commit()

        return user


class RefreshTokenExpiration(Base):
    """A refresh token expiration."""

    __tablename__ = "refresh_token_expiration"

    id = Column(UUIDType, default=generate_uuid4, primary_key=True)  # noqa: A003
    user_id = Column(Integer, ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="refresh_token_expirations")
    expires_at = Column(DateTime)
    audience = Column(Text)
