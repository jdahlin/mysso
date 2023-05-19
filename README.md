MySSO
=====

MySSO is a simple SSO server written in Python. It is a work in progress.
Requires Python 3.11, Django and authlib.

Features:
* OAuth2 Specs implemented: (see https://oauth.net/2/)
  * OAuth 2.0 Core (RFC 6749)
  * Bearer Token Usage (RFC 6750)
  * Token Revocation (RFC 7009)
  * PKCE: Proof Key for Code Exchange (RFC 7636)
  * Token Introspection (RFC 7662)
  * Authorization Server Metadata (RFC 8414)
  * JWT Profile for OAuth Access Tokens (RFC 9068)
  * JWT Authorization Request (RFC 9101)
* OAuth2 flows (authorization code, implicit, client credentials, refresh token, password)
* OpenID Connect flows (implicit and hybrid)
* Strong Password hashing using Argon2id
* Login, Signup and Content pages
* User portal (edit personal information)
* MFA (OTP, WebAuthn)
* Django Admin for Clients/Users/Authorization Codes and Tokens
* Pretty CLI for user management, client registration, etc. (via Typer)
* Multi-tenancy
* User management (CLI and Django Admin)
* User registration (CLI and Django Admin)
* mypy strict
* very strict ruffness (few exceptions)
* Email verification (not complete)

TODO:
* Portal: Change Picture
* Portal: Enable/Disable MFA devices
* Better test coverage
* SAML
* Write documentation and tutorial
* Docker compose file
* OAuth: Device Authorization Grant (RFC 8628)
* OAuth: Assertion Framework (RFC 7521)
* OAuth: Mutual TLS Bound Access Tokens (RFC 8705)
* OAuth: Pushed Authorization Requests (RFC 9126)
* OAuth: Dynamic Client Registration (RFC 7591)
* OAuth: Dynamic Client Management (RFC 7592)
* Throttling for guessing passwords etc

Integrations:
* OpenID Providers (via python-social?)
* Secret Storage (AWS KMS, GCP KMS, Azure Key Vault, Hashicorp Vault, etc.)
* SMS provider integration (e.g. AWS SNS, Twilio, GCP SMS, Azure SMS, etc.)
* Transactional email service providers (e.g django-anymail)
