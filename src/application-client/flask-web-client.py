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

SCOPES = "openid email profile"  # pwd_exp pwd_url

with (Path(__file__).parent / ".credentials.json").open() as f:
    data = json.load(f)
    client_data = data["authorization_code_grant"]
    client_id = client_data["client_id"]
    client_secret = client_data["client_secret"]

app = Flask(__name__)
app.config.update(
    {
        "PREFERRED_URL_SCHEME": "https",
    },
)
app.secret_key = data["secret"]


oauth = OAuth(app)
client = oauth.register(
    name="mysso",
    server_metadata_url=client_data["metadata_url"],
    client_id=client_id,
    client_secret=client_secret,
    client_kwargs={
        "scope": SCOPES,
    },
    code_challenge_method="S256",
    audience="https://dev-j-mmvo1r.auth0.com/api/v2/",
)

data = {}


@app.route("/")
def homepage() -> Response | str:
    user = session.get("user")
    if not user:
        return redirect("/login")

    # def generate_auth_string(user, token) -> bytes:

    # r = requests.post('https://sso.mac.nilhad.com/tenant/1/protocol/oauth2/introspect',
    #                   auth=('11a7a5e9-633e-4b15-b817-2579a556fdb7', '6skcme3V-ESCNRpUqR20Ng'))

    return render_template_string(
        """
<html>
<meta>
<style>
pre {
    font-size: 16px;
    overflow: auto;
    padding: 10px;
    background-color: #f8f8f8;
    border: 1px solid #ddd;
    white-space: pre-wrap;
}
</style>
</meta>
<body>
<section>
    <p>Requested Scopes: <code>{{ scopes }}</code></p>
</section>

<section>
    This is the content of the access token received from the OpenID Connect Provider:

    <pre id="oauth_token"></pre>
</section>

<section>
    <p>Click <a href="/logout">here</a> to logout.</p>
</section>

<script async defer>
var text = JSON.stringify({{ oauth_token|tojson }}, undefined, 2);
document.getElementById("oauth_token").textContent = text;
</script>
</body>
</html>
""",
        user=user,
        scopes=SCOPES,
        oauth_token=data.get("oauth_token"),
    )


@app.route("/login")
def login() -> Response:
    redirect_uri = url_for("auth", _external=True, _scheme="https")
    return cast(Response, client.authorize_redirect(redirect_uri))


@app.route("/d/auth/complete/google-oauth2")
def auth() -> Response:
    token = oauth.mysso.authorize_access_token()
    session["user"] = token["userinfo"]
    return redirect("/")


@app.route("/logout")
def logout() -> Response:
    session.pop("user", None)
    return redirect("/")
