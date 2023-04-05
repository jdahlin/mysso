from authlib.integrations.flask_client import OAuth
from flask import (
    Flask,
    redirect,
    render_template_string,
    session,
    url_for,
)

app = Flask(__name__)
app.secret_key = "!secret"

oauth = OAuth(app)
oauth.register(
    name="google",
    server_metadata_url="http://127.0.0.1:5000/.well-known/openid-configuration",
    client_id="application-service-1",
    client_secret="my secret",
    client_kwargs={
        "scope": "openid email profile",
    },
)

@app.route("/")
def homepage() -> str:
    user = session.get("user")
    return render_template_string("""
{% if user %}
<pre>
{{ user|tojson }}
</pre>
<a href="/logout">logout</a>
{% else %}
<a href="/login">login</a>
{% endif %}""", user=user)


@app.route("/login")
def login() -> None:
    redirect_uri = url_for("auth", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route("/d/auth/complete/google-oauth2")
def auth() -> None:
    token = oauth.google.authorize_access_token()
    session["user"] = token["userinfo"]
    return redirect("/")


@app.route("/logout")
def logout() -> None:
    session.pop("user", None)
    return redirect("/")
