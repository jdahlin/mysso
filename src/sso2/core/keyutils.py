"""This module contains public and private Jwk keys."""
import dataclasses
import enum
from functools import lru_cache
from pathlib import Path

from authlib.jose import JsonWebKey, RSAKey

key_dir = Path(__file__).parent.parent.parent.parent / "keys"


class JwsAlgorithm(enum.StrEnum):
    EdDSA = "EdDSA"
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


@lru_cache
def get_private_key_from_path(path: str) -> RSAKey:
    """Return the private key used to sign JWTs."""
    with (key_dir / path).open() as f:
        private_key = JsonWebKey.import_key(f.read())
        if not private_key.private_key:
            raise AssertionError("Private key is not private")
        return private_key


@lru_cache
def get_public_key_from_path(path: str) -> RSAKey:
    """Return the public key used to verify JWTs."""
    with (key_dir / path).open() as f:
        public_key = JsonWebKey.import_key(f.read())
        if public_key.private_key:
            raise AssertionError("Public key is not public")
        return public_key


@dataclasses.dataclass
class StoredKey:
    key: RSAKey
    path: Path
    private: bool = True

    def write_to_path(self) -> None:
        with self.path.open("wb") as f:
            f.write(self.key.as_pem(is_private=self.private))

        permission = 420 if self.private else 384
        self.path.chmod(permission)


def create_key_pair(
    basename: str,
    algorithm: JwsAlgorithm,
) -> tuple[StoredKey, StoredKey]:
    key_dir.mkdir(exist_ok=True)

    private_key_path = key_dir / (basename + "-private_key.pem")
    generate_new_key = True
    if private_key_path.exists():
        private_jwk = get_private_key_from_path(str(private_key_path))
        generate_new_key = False
    else:
        assert algorithm == "RS256"
        private_jwk = JsonWebKey.generate_key(
            kty="RSA",
            crv_or_size=2048,
            is_private=True,
        )

    private = StoredKey(
        key=private_jwk,
        path=private_key_path,
    )

    public = StoredKey(
        key=private_jwk,
        path=key_dir / (basename + "-public_key.pem"),
        private=False,
    )
    if generate_new_key:
        private.write_to_path()
        public.write_to_path()
    return public, private
