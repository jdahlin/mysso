import uuid

from sqlalchemy import Text
from sqlalchemy.orm import DeclarativeBase

from sso.hashutils import get_password_hasher

UUIDType = Text(length=36)
hasher = get_password_hasher()


def generate_uuid4() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass
