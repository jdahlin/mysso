from typing import TypedDict, cast

from pydantic import BaseModel
from starlette.responses import Response

from sso.app import app
from sso.models.tenant import Tenant


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


@app.get("/tenant/{tenant_id:str}.well-known/jwks.json")
def jwks_json(tenant_id: str, response: Response) -> JWKSResponse:
    tenant = Tenant.get_or_404(tenant_id=tenant_id)
    jwk_set = tenant.get_public_key().as_jwks()
    response.headers["Cache-Control"] = (
        "public, max_age=3600, " "stale-while-revalidate=3600, " "stale-if-error=3600"
    )
    return cast(JWKSResponse, jwk_set)
