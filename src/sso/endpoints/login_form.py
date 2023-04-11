from starlette.responses import HTMLResponse, RedirectResponse, Response

from sso.app import app
from sso.models import Tenant, User
from sso.tokens import TokenContext


def render_login_form(
    tenant_id: str,
    state: str | None,
    redirect_uri: str | None,
) -> HTMLResponse:
    return HTMLResponse(
        f"""<html>
<head>
    <style>
    body {{
      margin: 0 auto;
      background-color: dimgrey;
      color: white;
    }}
    .container {{
      margin: 30% auto;
      display: block;
      width: 500px;
      text-align:center;
    }}

    .container input {{
      margin-bottom: 10px;
    }}
    </style>
</head>
<body>
<div class="container">
    <h1>Login to SSO</h1>
    <section>
        <form action="/tenant/{tenant_id}/login-form" method="get">
            <input #username type="text" name="username" placeholder="Username or email"
                   autofocus autocomplete="on" /><br/>
            <input #password type="password" name="password"
                   placeholder="Password"/><br/>
            <input type="hidden" name="state" value="{state}"/>
            <input type="hidden" name="redirect_uri" value="{redirect_uri}"/>
            <button type="submit" role="button"/>Login</button>
        </form>
    </section>
</div>
</body>
</html>
""",
    )


@app.get("/tenant/{tenant_id:str}/login-form")
def submit_login_form(
    tenant_id: str,
    state: str,
    username: str,
    password: str,
    redirect_uri: str,
) -> Response:
    tenant = Tenant.get_or_404(tenant_id=tenant_id)
    user = User.try_password_login(
        email=username,
        password=password,
        tenant=tenant,
    )

    code = TokenContext(tenant=tenant).create_authorization_code(user=user)
    return RedirectResponse(f"{redirect_uri}?code={code}&state={state}")
