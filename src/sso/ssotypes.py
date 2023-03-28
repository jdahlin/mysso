"""This module contains all the types used in the SSO service."""
from typing import NewType

Audience = NewType("Audience", str)
Email = NewType("Email", str)
PasswordHashedInSha256 = NewType("PasswordHashedInSha256", str)
Base64EncodedToken = NewType("Base64EncodedToken", str)
