from pydantic import BaseModel

from sso.app import app
from sso.models import User
from sso.ssotypes import Audience, Base64EncodedToken
from sso.tokens import TokenContext, TokenPairResponse


class RefreshRequest(BaseModel):
    refresh_token: Base64EncodedToken
    audience: Audience


@app.get("/refresh")
def refresh(body: RefreshRequest) -> TokenPairResponse:
    user = User.try_refresh_token_login(
        insecure_token_payload=body.refresh_token,
        audience=body.audience,
    )
    token_context = TokenContext(user=user, audience=body.audience)
    access_token, refresh_token = token_context.create_tokens()
    return TokenPairResponse(
        access_token=Base64EncodedToken(str(access_token)),
        refresh_token=Base64EncodedToken(str(refresh_token)),
    )
