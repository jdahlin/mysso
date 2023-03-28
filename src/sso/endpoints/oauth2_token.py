from typing import Annotated

from fastapi import Depends, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

from sso.app import app
from sso.exceptions import (
    BadRequestError,
    EndpointNotImplementedError,
    UnsupportedGrantTypeError,
)
from sso.models import User
from sso.ssotypes import Audience, Base64EncodedToken, Email, PasswordHashedInSha256
from sso.tokens import TokenContext

security = HTTPBasic()


# Access Token Response
# https://www.rfc-editor.org/rfc/rfc6749#section-4.3.3
class OAuth2TokenResponse(BaseModel):
    access_token: Base64EncodedToken
    refresh_token: Base64EncodedToken
    token_type: str
    expires_in: int


@app.post("/oauth2/token")
async def oauth2_token(   # noqa: PLR0913
        credentials: Annotated[HTTPBasicCredentials, Depends(security)],
        grant_type: Annotated[str, Form()],
        scope: Annotated[Audience, Form()],
        username: Annotated[Email, Form()] | None = None,
        password: Annotated[PasswordHashedInSha256, Form()] | None = None,
        refresh_token: Annotated[str, Form()] | None = None,
        redirect_uri_port: Annotated[int, Form()]  | None = None,
) -> OAuth2TokenResponse:
    """This endpoint is used to obtain an access token and a refresh token."""
    match grant_type:
        # OAuth2 Access Token Request
        # https://www.rfc-editor.org/rfc/rfc6749#section-4.1.3
        case "authorization_code":
            raise EndpointNotImplementedError(grant_type)
        # OAuth2 Resource Owner Password Credentials Grant
        # https://www.rfc-editor.org/rfc/rfc6749#section-4.3
        case "password":
            if username is None:
                raise BadRequestError("username is required")
            if password is None:
                raise BadRequestError("password is required")
            user = User.try_password_login(
                email=username,
                hashed_password=password,
                audience=scope)
        # OAuth2 Client Credentials Grant
        # https://www.rfc-editor.org/rfc/rfc6749#section-4.4
        case "client_credentials":
            user = User.try_password_login(
                email=credentials.username,
                hashed_password=credentials.password,
                audience=scope)
        # OAuth2 Refreshing an Access Token
        # https://www.rfc-editor.org/rfc/rfc6749#section-6
        case "refresh_token":
            if refresh_token is None:
                raise BadRequestError("refresh_token is required")
            user = User.try_refresh_token_login(
                insecure_token_payload=refresh_token,
                audience=scope,
           )
        case _:
            raise UnsupportedGrantTypeError(grant_type)

    token_context = TokenContext(user=user, audience=scope)
    access_token_jwt, refresh_token_jwt = token_context.create_tokens()
    return OAuth2TokenResponse(
        access_token=Base64EncodedToken(str(access_token_jwt)),
        refresh_token=Base64EncodedToken(str(refresh_token_jwt)),
        expires_in=token_context.access_token_lifetime,
        token_type="bearer",   # noqa: S106
    )
