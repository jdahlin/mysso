import time

import requests
import typer
from requests import Session
from requests_auth import OAuth2ClientCredentials

from sso.hashutils import get_password_hasher

APPLICATION_API_URL = "http://localhost:5001"
SSO_API_URL = "http://127.0.0.1:5000"
SSO_AUTH_EMAIL = "jdahlin@gmail.com"
SSO_AUTH_SECRET = "foobar"


def main(
    application_name: str = "application-service-1",
    application_api_url: str = APPLICATION_API_URL,
    sso_api_url: str = SSO_API_URL,
    client_id: str = SSO_AUTH_EMAIL,
    client_secret: str = SSO_AUTH_SECRET,
) -> None:
    session = Session()
    session.auth = OAuth2ClientCredentials(
        token_url=f"{sso_api_url}/oauth2/token",
        client_id=client_id,
        client_secret=get_password_hasher().hash_password(client_secret),
        scope=application_name,
    )

    while True:
        r = session.get(f"{application_api_url}/protected_endpoint")
        try:
            r.raise_for_status()
            print(f"Request successful. Response was: '{r.json()}'")
        except requests.exceptions.HTTPError as e:
            print(f"Request was not successful. Error was {e.response.content}")

        print("sleep")
        time.sleep(5)


if __name__ == "__main__":
    typer.run(main)
