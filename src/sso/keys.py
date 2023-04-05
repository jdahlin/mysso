"""This module contains public and private Jwk keys."""
import dataclasses
import enum
from functools import lru_cache
from pathlib import Path

from jwskate import Jwk

from sso.settings import JWT_ALGORITHM

key_dir = Path(__file__).parent.parent.parent / "keys"


class Algorithm(enum.StrEnum):
    ES256 = "ES256"
    ES384 = "ES384"
    ES512 = "ES512"
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    PS256 = "PS256"
    PS384 = "PS384"
    PS512 = "PS512"
    RS256 = "RS256"
    RS384 = "RS384"
    RS512 = "RS512"
    EdDSA = "EdDSA"


@lru_cache
def get_private_key() -> Jwk:
    """Return the private key used to sign JWTs."""
    with (key_dir / "private_key.pem").open() as f:
        private_key = Jwk.from_pem_key(f.read())
        if not private_key.is_private:
            raise AssertionError("Private key is not private")
        return private_key


@lru_cache
def get_public_key() -> Jwk:
    """Return the public key used to verify JWTs."""
    with (key_dir / "public_key.pem").open() as f:
        public_key = Jwk.from_pem_key(f.read())
        if public_key.is_private:
            raise AssertionError("Public key is not public")
        return public_key.with_usage_parameters(alg=JWT_ALGORITHM, with_use=True)


@dataclasses.dataclass
class StoredKey:
    key: Jwk
    path: Path
    public: bool = False

    def write_to_path(self) -> None:
        with self.path.open("wb") as f:
            f.write(self.key.to_pem(""))
        permission = 420 if self.public else 384
        self.path.chmod(permission)


def create_key_pair(basename: str, algorithm: Algorithm) -> tuple[StoredKey, StoredKey]:
    private_jwk = (
        Jwk.generate_for_alg(algorithm).with_kid_thumbprint().with_usage_parameters()
    )
    key_dir.mkdir(exist_ok=True)

    private = StoredKey(
        key=private_jwk,
        path=key_dir / (basename + "-private_key.pem"),
    )
    public = StoredKey(
        key=private_jwk.public_jwk(),
        path=key_dir / (basename + "-public_key.pem"),
        public=True,
    )

    private.write_to_path()
    public.write_to_path()
    return public, private
