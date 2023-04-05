import bcrypt


def hash_password(password: str, salt: str) -> str:
    """Hash a password."""
    return bcrypt.hashpw(password.encode(), salt).decode()
