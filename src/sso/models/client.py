from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sso.models.base import Base, UUIDType, generate_uuid4

if TYPE_CHECKING:
    from sso.models.tenant import Tenant


class Client(Base):
    """A Client that can be logged into."""

    __tablename__ = "client"

    id = mapped_column(UUIDType, default=generate_uuid4, primary_key=True)  # noqa: A003

    name = mapped_column(Text, unique=True, index=True)

    tenant_id = mapped_column(UUIDType, ForeignKey("tenant.id"))

    tenant: Mapped["Tenant"] = relationship(back_populates="clients")

    secret = mapped_column(Text)
