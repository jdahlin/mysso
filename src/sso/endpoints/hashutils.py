import hashlib
from typing import Literal

HashAlgorithm = Literal[
    "blake2b",
    "blake2s",
    "md5",
    "sha1",
    "sha224",
    "sha256",
    "sha384",
    "sha512",
    "sha3_224",
    "sha3_256",
    "sha3_384",
    "sha3_512",
    "shake_128",
    "shake_256",
]


def hash_password(password: str, algorithm: HashAlgorithm = "sha256") -> str:
    """Hash a password using the given algorithm."""
    hash_ = hashlib.new(algorithm)
    hash_.update(password.encode())
    return hash_.hexdigest()
