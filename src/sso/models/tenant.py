from typing import TYPE_CHECKING

from fastapi_sqlalchemy import db
from jwskate import Jwk
from sqlalchemy import Enum, Text
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Mapped, mapped_column, relationship
from starlette import status
from starlette.exceptions import HTTPException

from sso.keys import (
    JwsAlgorithm,
    create_key_pair,
    get_private_key_from_path,
    get_public_key_from_path,
)
from sso.models.base import Base, UUIDType, generate_uuid4
from sso.models.client import Client
from sso.settings import JWT_ISSUER

if TYPE_CHECKING:
    from sso.models.user import User


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
