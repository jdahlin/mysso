MySSO
=====

MySSO is a simple SSO server written in Python. It is a work in progress. 
Requires Python 3.11, Django and authlib.

Features:
* OAuth2 and OpenID Connect (authorization code flow)
* Simple HTML Login dialog
* Simple Consent Screen
* Pretty CLI for user management, client registration, etc. (via Typer)
* Multi-tenancy
* User management (CLI and Django Admin)
* User registration (CLI and Django Admin)
* mypy strict
* very strict ruffness (few exceptions)

TODO:
* Better test coverage
* sqladmin or port over to django-admin
* SAML
* Write documentation and tutorial
* JavaScript example
* Docker compose file
* Require PostgreSQL instead of SQLite
* MFA (OTP, U2F, etc.)
* WebAuthn
* User profile
* User registration
* Email verification

Integrations:
* OpenID Providers (via python-social?)
* Secret Storage (AWS KMS, GCP KMS, Azure Key Vault, Hashicorp Vault, etc.)
* SMS provider integration (e.g. AWS SNS, Twilio, GCP SMS, Azure SMS, etc.)
* Transactional email service providers (e.g django-anymail)

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
