MySSO
=====

MySSO is a simple SSO server written in Python. It is a work in progress. 
Requires Python 3.11, Django and authlib.

Features:
* OAuth2 flows (authorization code, implicit, client credentials, refresh token, password)
* OAuth2 token introspection
* OAuth2 token revocation
* OAuth2 JWT Access Tokens (RFC9068)
* OpenID Connect discovery
* OpenID Connect nonce/PKCE
* OpenID Connect flows (implicit and hybrid)
* Strong Password hashing using Argon2id
* Login, Signup and Content pages
* User portal
* MFA (OTP, WebAuthn)
* Django Admin for Clients/Users/Authorization Codes and Tokens
* Pretty CLI for user management, client registration, etc. (via Typer)
* Multi-tenancy
* User management (CLI and Django Admin)
* User registration (CLI and Django Admin)
* mypy strict
* very strict ruffness (few exceptions)

TODO:
* Portal: Change Picture
* Portal: Edit personal information
* Portal: Manage MFA devices
* Better test coverage
* SAML
* Write documentation and tutorial
* Docker compose file
* Email verification

Integrations:
* OpenID Providers (via python-social?)
* Secret Storage (AWS KMS, GCP KMS, Azure Key Vault, Hashicorp Vault, etc.)
* SMS provider integration (e.g. AWS SNS, Twilio, GCP SMS, Azure SMS, etc.)
* Transactional email service providers (e.g django-anymail)

* Demo/Tutorial
====

Needs Python 3.11

TODO: Write better and a more thorough explanation of the demo.

* `pip install .`
* `ssotool init`
* `ssotool user create bob@example.com`
  * Enter `secret` as password
* In one terminal run:
  * `python -muvicorn --app-dir=src sso.app:app --port 5000`
* In another terminal run
  * `FLASK_DEBUG=1 FLASK_APP=src/application-service/application.py flask run --port 5001`
* In another terminal run
  * `python src/application-client/client.py --client-id bob@example.com --client-secret secret`
