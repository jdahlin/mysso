from pydantic import BaseModel

from sso.app import app
from sso.exceptions import EndpointNotImplementedError


class OAuth2AuthorizeRequest(BaseModel):
    response_type: str
    client_id: str
    redirect_uri: str
    scope: str | None = None
    state: str | None = None


class OAuth2AuthorizeResponse(BaseModel):
    pass


# OAuth2 Authorization Request
# https://www.rfc-editor.org/rfc/rfc6749#section-4.2.1
@app.get("/oauth2/authorize")
def oauth2_authorize(response_type: str,  # noqa: PLR0913
                     client_id: str,
                     redirect_uri: str | None = None,
                     client_secret: str | None = None,
                     scope: str | None = None,
                     state: str | None = None) -> OAuth2AuthorizeResponse:
    raise EndpointNotImplementedError
