from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sso.models.base import Base, UUIDType, generate_uuid4

if TYPE_CHECKING:
    from sso.models.tenant import Tenant


class AuthConnection(Base):
    """Connects to a third-party provider that is used to authenticate a user ."""

    __tablename__ = "auth_connection"

    id = mapped_column(UUIDType, default=generate_uuid4, primary_key=True)  # noqa: A003

    tenant_id = mapped_column(UUIDType, ForeignKey("tenant.id"))

    tenant: Mapped["Tenant"] = relationship(back_populates="auth_connections")

    # FIXME: type = openid/oauth2
    name = mapped_column(Text, unique=True, index=True)

    issuer_url = mapped_column(Text)

    client_id = mapped_column(Text)

    client_secret = mapped_column(Text)
