from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sso.models.base import Base, UUIDType, generate_uuid4

if TYPE_CHECKING:
    from sso.models.user import User


class PersistentToken(Base):

    """A persistent token expiration.

    This is used to store refresh tokens and authorization codes.
    """

    __tablename__ = "persistent_token"

    id = mapped_column(UUIDType, default=generate_uuid4, primary_key=True)  # noqa: A003
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship(back_populates="refresh_token_expirations")
    expires_at = mapped_column(DateTime)
