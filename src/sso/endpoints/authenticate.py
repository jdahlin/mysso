"""This module contains the authenticate endpoint."""
from pydantic import BaseModel

from sso.app import app
from sso.models import User
from sso.ssotypes import Audience, Base64EncodedToken, Email, PasswordHashedInSha256
from sso.tokens import TokenContext, TokenPairResponse


class AuthenticateRequest(BaseModel):
    email: Email
    hashed_password: PasswordHashedInSha256
    audience: Audience


@app.post("/authenticate")
def authenticate(body: AuthenticateRequest) -> TokenPairResponse:
    """This endpoint is used to obtain an access token and a refresh token."""
    user = User.try_password_login(
        email=body.email,
        hashed_password=body.hashed_password,
        audience=body.audience,
    )

    token_context = TokenContext(user=user, audience=body.audience)
    access_token, refresh_token = token_context.create_tokens()
    return TokenPairResponse(
        access_token=Base64EncodedToken(str(access_token)),
        refresh_token=Base64EncodedToken(str(refresh_token)),
    )
