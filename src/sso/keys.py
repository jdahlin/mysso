"""This module contains public and private Jwk keys."""
from functools import lru_cache
from pathlib import Path

from jwskate import Jwk

from sso.settings import JWT_ALGORITHM

key_dir = Path(__file__).parent.parent.parent / "keys"


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
