import json
from pathlib import Path

from authlib.integrations.httpx_client import OAuth2Client

with (Path(__file__).parent / ".credentials.json").open() as f:
    data = json.load(f)["password_grant"]
    client_id = data["client_id"]
    client_secret = data["client_secret"]
    username = data["username"]
    password = data["password"]

client = OAuth2Client(client_id, client_secret, scope="openid email scope")
token = client.fetch_token(
    "http://127.0.0.1:5000/oauth/token",
    username=username,
    password=password,
    grant_type="password",
)
print(token)
