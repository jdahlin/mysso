import time
from typing import TYPE_CHECKING

from fastapi_sqlalchemy import db
from jwskate import InvalidClaim, SignedJwt
from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from sso.exceptions import UnauthorizedError
from sso.models.base import Base, UUIDType, generate_uuid4, hasher

if TYPE_CHECKING:
    from sso.models.persistent_token import PersistentToken
    from sso.models.tenant import Tenant


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
    tenant: Mapped["Tenant"] = relationship(back_populates="users")

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
        tenant: "Tenant",
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
        tenant: "Tenant",
    ) -> "User":
        jwt = SignedJwt(insecure_token_payload)
        try:
            jwt.validate(jwk=tenant.get_public_key(), issuer=tenant.get_issuer())
        except InvalidClaim as e:
            raise UnauthorizedError("Invalid refresh token") from e

        from sso.models.persistent_token import PersistentToken

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
