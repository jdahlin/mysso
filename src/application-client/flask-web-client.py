import json
from pathlib import Path
from typing import cast

from authlib.integrations.flask_client import OAuth
from flask import (
    Flask,
    redirect,
    render_template_string,
    session,
    url_for,
)
from werkzeug import Response

app = Flask(__name__)
app.secret_key = "!secret"

with (Path(__file__).parent / ".credentials.json").open() as f:
    data = json.load(f)["authorization_code_grant"]
    client_id = data["client_id"]
    client_secret = data["client_secret"]

oauth = OAuth(app)
oauth.register(
    name="mysso",
    server_metadata_url="http://sso.lvh.me:5000/tenant/master/.well-known/openid-configuration",
    client_id=client_id,
    client_secret=client_secret,
    client_kwargs={
        "scope": "openid email profile",
    },
    code_challenge_method="S256",
)


@app.route("/")
def homepage() -> Response | str:
    user = session.get("user")
    if not user:
        return redirect("/login")
    return render_template_string(
        """
<pre>
{{ user|tojson }}
</pre>
<a href="/logout">logout</a>
""",
        user=user,
    )


@app.route("/login")
def login() -> Response:
    redirect_uri = url_for("auth", _external=True)
    print("REDIRECT TO", redirect_uri)
    return cast(Response, oauth.mysso.authorize_redirect(redirect_uri))


@app.route("/d/auth/complete/google-oauth2")
def auth() -> Response:
    token = oauth.mysso.authorize_access_token()
    print(oauth.mysso.token)
    session["user"] = token["userinfo"]
    return redirect("/")


@app.route("/logout")
def logout() -> Response:
    session.pop("user", None)
    return redirect("/")
