from fastapi_sqlalchemy import db
from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound
from starlette import status
from starlette.exceptions import HTTPException
from starlette.responses import Response

from sso.app import app
from sso.endpoints.login_form import render_login_form
from sso.exceptions import EndpointNotImplementedError
from sso.models.client import Client
from sso.models.tenant import Tenant


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
@app.get("/tenant/{tenant_id}/oauth2/authorize")
def oauth2_authorize(
    tenant_id: str,
    response_type: str,
    client_id: str,
    response_mode: str | None = None,
    redirect_uri: str | None = None,
    scope: str | None = None,
    state: str | None = None,
    code_challenge: str | None = None,
    code_challenge_method: str | None = None,
) -> Response:
    tenant = Tenant.get_or_404(tenant_id=tenant_id)
    match response_type:
        case "code":
            if not response_mode:
                response_mode = "query"
        case "token":
            # FIXME: implement response_type=token
            raise EndpointNotImplementedError

    # FIXME: implement response_mode=fragment

    print(
        f"{tenant_id=} {client_id=} {response_type=} {response_mode=} {redirect_uri=}",
    )
    try:
        db.session.query(Client).filter_by(id=client_id, tenant=tenant).one()
    except NoResultFound as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        ) from e

    # FIXME: validate redirect_uri against a list of allowed redirect_uris
    if response_mode == "query":
        return render_login_form(
            tenant_id=tenant_id,
            state=state,
            redirect_uri=redirect_uri,
        )
    else:
        raise EndpointNotImplementedError(f"{response_mode=}")
