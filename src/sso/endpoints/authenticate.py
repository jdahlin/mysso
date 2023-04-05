"""This module contains the authenticate endpoint."""
from pydantic import BaseModel

from sso.app import app
from sso.models import User
from sso.passwordutils import hash_password
from sso.ssotypes import Audience, Base64EncodedToken, Email, PasswordHashedInSha256
from sso.tokens import TokenContext, TokenPairResponse


class AuthenticateRequest(BaseModel):
    email: Email
    hashed_password: PasswordHashedInSha256
    audience: Audience


@app.post("/<tenant_id:str>/authenticate")
def authenticate(tenant_id: str, body: AuthenticateRequest) -> TokenPairResponse:
    """This endpoint is used to obtain an access token and a refresh token."""
    tenant = ...
    user = User.try_password_login(
        email=body.email,
        hashed_password=hash_password(body.hashed_password, tenant.password_salt),
        audience=body.audience,
    )

    token_context = TokenContext(user=user, audience=body.audience)
    access_token, refresh_token = token_context.create_tokens()
    return TokenPairResponse(
        access_token=Base64EncodedToken(str(access_token)),
        refresh_token=Base64EncodedToken(str(refresh_token)),
    )
