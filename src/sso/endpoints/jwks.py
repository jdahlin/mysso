from typing import TypedDict, cast

from pydantic import BaseModel
from starlette.responses import Response

from sso.app import app
from sso.keys import get_public_key


class JWKSItem(TypedDict):
    kty: str
    crv: str
    x: str
    y: str
    kid: str
    use: str
    alg: str


class JWKSResponse(BaseModel):
    keys: list[JWKSItem]


@app.get("/.well-known/jwks.json")
def jwks_json(response: Response) -> JWKSResponse:
    jwk_set = get_public_key().as_jwks()
    response.headers["Cache-Control"] = "public, max_age=3600, " \
                                        "stale-while-revalidate=3600, " \
                                        "stale-if-error=3600"
    return cast(JWKSResponse, jwk_set)
