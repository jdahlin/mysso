MySSO
=====

MySSO is a simple SSO server written in Python. It is a work in progress. 
Requires Python 3.11, FastAPI, SQLAlchemy, passlib and jwskate.

Features:
* OAuth2 and OpenID Connect (authorization code flow)
* Simple HTML Login dialog
* Pretty CLI for user management, client registration, etc. (via Typer)
* argon2 and bcrypt password hashing (via passlib)
* Multi-tenancy
* User management (CLI only)
* User registration (CLI only)
* mypy strict
* very strict ruffness (few exceptions)

TODO:
* Investigate authlib
* Better test coverage
* sqladmin or port over to django-admin
* OpenID Providers (via python-social?)
* SAML
* Write documentation and tutorial
* JavaScript example
* Docker compose file
* Require PostgreSQL instead of SQLite
* Secret Storage (AWS KMS, GCP KMS, Azure Key Vault, Hashicorp Vault, etc.)
* MFA (OTP, U2F, etc.)
* WebAuthn
* OAuth2 Client Credentials Flow
* OAuth2 Resource Owner Password Credentials Flow
* OAuth2 Implicit Flow

Demo/Tutorial 
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
