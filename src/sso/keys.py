"""This module contains public and private Jwk keys."""
from functools import lru_cache

from jwskate import Jwk

from sso.settings import JWT_ALGORITHM


@lru_cache
def get_private_key() -> Jwk:
    """Return the private key used to sign JWTs."""
    with open("keys/private_key.pem") as f:
        private_key = Jwk.from_pem_key(f.read())
        if private_key.is_private:
            raise AssertionError("Private key is not private")
        return private_key


@lru_cache
def get_public_key() -> Jwk:
    """Return the public key used to verify JWTs."""
    with open("keys/public_key.pem") as f:
        pubic_key = Jwk.from_pem_key(f.read())
        if not pubic_key.is_private:
            raise AssertionError("Public key is not public")
        return pubic_key.with_usage_parameters(alg=JWT_ALGORITHM, with_use=True)
