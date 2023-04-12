import datetime
import logging
from typing import Annotated, cast

from fastapi import Depends, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi_sqlalchemy import db
from jwskate import InvalidClaim, Jwt, SignedJwt
from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound

from sso.app import app
from sso.exceptions import (
    BadRequestError,
    EndpointNotImplementedError,
    OAuth2InvalidRequestError,
    UnauthorizedError,
    UnsupportedGrantTypeError,
)
from sso.models.persistent_token import PersistentToken
from sso.models.tenant import Tenant
from sso.models.user import User
from sso.ssotypes import Base64EncodedToken, Email, PasswordHashedInSha256
from sso.tokens import TokenContext

security = HTTPBasic()


# Access Token Response
# https://www.rfc-editor.org/rfc/rfc6749#section-4.3.3
class OAuth2TokenResponse(BaseModel):
    access_token: Base64EncodedToken
    refresh_token: Base64EncodedToken
    token_type: str
    expires_in: int
    userinfo: dict[str, str]


def validate_authorization_code(*, tenant: Tenant, insecure_token_payload: str) -> User:
    jwt = SignedJwt(insecure_token_payload)
    try:
        jwt.validate(jwk=tenant.get_public_key(), issuer=tenant.get_issuer())
    except InvalidClaim as e:
        logging.exception("invalid claim")
        raise UnauthorizedError("Invalid code") from e
    try:
        user = db.session.query(User).filter_by(id=jwt.subject, is_active=True).one()
    except NoResultFound as e:
        logging.exception("invalid claim")
        raise UnauthorizedError("Invalid code") from e

    try:
        persistent_token = (
            db.session.query(PersistentToken).filter_by(id=jwt.jwt_token_id).one()
        )
    except NoResultFound as e:
        logging.exception("invalid claim")
        raise UnauthorizedError("Invalid code") from e
    else:
        if persistent_token.expires_at.timestamp() > Jwt.timestamp():
            raise UnauthorizedError("Code expired")
        db.session.delete(persistent_token)
        db.session.commit()
    return user


@app.post("/tenant/{tenant_id:str}/oauth2/token")
async def oauth2_token(
    tenant_id: str,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    grant_type: Annotated[str, Form()],
    code: str | None = Form(None),
    username: Annotated[Email, Form()] | None = None,
    password: Annotated[PasswordHashedInSha256, Form()] | None = None,
    refresh_token: Annotated[str, Form()] | None = None,
    redirect_uri: Annotated[str, Form()] | None = None,
    redirect_uri_port: Annotated[int, Form()] | None = None,
) -> OAuth2TokenResponse:
    tenant = Tenant.get_or_404(tenant_id=tenant_id)
    """This endpoint is used to obtain an access token and a refresh token."""
    match grant_type:
        # OAuth2 Access Token Request
        # https://www.rfc-editor.org/rfc/rfc6749#section-4.1.3
        case "authorization_code":
            if code is None:
                raise OAuth2InvalidRequestError(
                    "code is required when grant_type is authorization_code",
                )
            user = validate_authorization_code(
                insecure_token_payload=code,
                tenant=tenant,
            )
            # FIXME: Delete persistent token associated with the code
        # OAuth2 Resource Owner Password Credentials Grant
        # https://www.rfc-editor.org/rfc/rfc6749#section-4.3
        case "password":
            if username is None:
                raise BadRequestError("username is required")
            if password is None:
                raise BadRequestError("password is required")
            user = User.try_password_login(
                email=username,
                password=password,
                tenant=tenant,
            )
        # OAuth2 Client Credentials Grant
        # https://www.rfc-editor.org/rfc/rfc6749#section-4.4
        case "client_credentials":
            # Use credentials.username, credentials.password
            raise EndpointNotImplementedError
        # OAuth2 Refreshing an Access Token
        # https://www.rfc-editor.org/rfc/rfc6749#section-6
        case "refresh_token":
            if refresh_token is None:
                raise BadRequestError("refresh_token is required")
            user = User.try_refresh_token_login(
                insecure_token_payload=refresh_token,
                tenant=tenant,
            )
        case _:
            raise UnsupportedGrantTypeError(grant_type)

    token_context = TokenContext(tenant=tenant)
    access_token_jwt, refresh_token_jwt = token_context.create_tokens(user=user)
    assert access_token_jwt.expires_at is not None
    expires = (
        access_token_jwt.expires_at.timestamp()
        - datetime.datetime.now(datetime.UTC).timestamp()
    )
    return OAuth2TokenResponse(
        access_token=Base64EncodedToken(str(access_token_jwt)),
        refresh_token=Base64EncodedToken(str(refresh_token_jwt)),
        expires_in=int(expires),
        token_type="bearer",  # noqa: S106
        userinfo={"id": cast(str, user.id), "email": cast(str, user.email)},
    )
