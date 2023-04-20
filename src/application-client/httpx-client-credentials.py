import json
from pathlib import Path

from authlib.integrations.httpx_client import OAuth2Client

with (Path(__file__).parent / ".credentials.json").open() as f:
    data = json.load(f)["client_credentials_grant"]
    client_id = data["client_id"]
    client_secret = data["client_secret"]
    username = data["username"]
    password = data["password"]

client = OAuth2Client(client_id, client_secret)
token = client.fetch_token(
    "http://localhost:5000/oauth/token",
    username=username,
    password=password,
    grant_type="client_credentials",
)

print(token)
