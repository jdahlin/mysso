from dataclasses import dataclass, field
from functools import lru_cache
from typing import TYPE_CHECKING

from sso.settings import PASSWORD_HASH_ROUNDS, PASSWORD_HASH_SCHEME

if TYPE_CHECKING:
    from passlib.context import CryptContext


# References
# - https://passlib.readthedocs.io/en/stable/narr/quickstart.html
# - https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Password_Storage_Cheat_Sheet.md


@dataclass
class PasswordHasher:
    schema: str
    rounds: int | None = None
    _cc: "CryptContext | None" = field(default=None, init=False)

    @property
    def cc(self) -> "CryptContext":
        if self._cc is None:
            from passlib.context import CryptContext

            kwargs = {}
            if self.rounds is not None:
                kwargs[f"{self.schema}__rounds"] = self.rounds
            self._cc = CryptContext(schemes=[self.schema])
            self._cc.update(kwargs)

        return self._cc

    def hash_password(self, password: str) -> str:
        return self.cc.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.cc.verify(password, hashed_password)

    def dummy_verify(self) -> bool:
        return bool(self.cc.dummy_verify())


@lru_cache
def get_password_hasher() -> PasswordHasher:
    return PasswordHasher(
        schema=PASSWORD_HASH_SCHEME,
        rounds=PASSWORD_HASH_ROUNDS,
    )
