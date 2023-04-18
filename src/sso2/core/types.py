from typing import Any, TypedDict

from django.http import HttpRequest

from sso2.core.models.user_model import User


class HttpRequestWithUser(HttpRequest):
    user: User


class JwtConfig(TypedDict):
    key: dict[str, Any]
    alg: str
    iss: str
    exp: int
