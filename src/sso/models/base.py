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


def load_all_models() -> None:
    import importlib
    from pathlib import Path

    model_files = list((Path(__file__).parent).glob("*.py"))
    for file in model_files:
        if file.stem in ["base", "__init__"]:
            continue
        print(file)
        importlib.import_module(f"sso.models.{file.stem}")
