# Generated by Django 4.2 on 2023-04-29 12:05

import authlib.oauth2.rfc6749.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import sso2.core.timeutils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("core", "0012_auto_20230429_1157"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    state_operations = [
        migrations.CreateModel(
            name="OAuth2Token",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("client_id", models.CharField(db_index=True, max_length=48)),
                ("token_type", models.CharField(max_length=40)),
                ("access_token", models.CharField(max_length=255, unique=True)),
                ("refresh_token", models.CharField(db_index=True, max_length=255)),
                ("scope", models.TextField(default="")),
                ("revoked", models.BooleanField(default=False)),
                (
                    "issued_at",
                    models.IntegerField(default=sso2.core.timeutils.now_timestamp),
                ),
                ("expires_in", models.IntegerField(default=0)),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "OAuth2 Token",
                "verbose_name_plural": "OAuth2 Tokens",
            },
            bases=(models.Model, authlib.oauth2.rfc6749.models.TokenMixin),
        ),
        migrations.CreateModel(
            name="OAuth2Client",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("client_name", models.TextField()),
                (
                    "grant_type",
                    models.TextField(
                        choices=[
                            ("authorization_code", "Authorization Code"),
                            (
                                "client_credentials",
                                "Client Credentials (server to server)",
                            ),
                            (
                                "urn:ietf:params:oauth:grant-type:device_code",
                                "Device code",
                            ),
                            ("implicit", "Implicit (legacy)"),
                            ("password", "Password (legacy)"),
                            ("refresh_token", "Refresh Token"),
                        ],
                        default="",
                        help_text='\n    OAuth2/OpenID Connect grant types. Recommended grant types are:<br>\n    <ul>\n    <li><a href="https://oauth.net/2/grant-types/authorization-code/">\n    authorization_code</a> (optionally with\n    <a href="https://oauth.net/2/pkce/">PKCE</a>)</li>\n    <li><a href="https://oauth.net/2/grant-types/refresh-token/">\n    refresh_token</a></li>\n    <li><a href="https://oauth.net/2/grant-types/device-code/">\n    device code</a></li>\n    <li><a href="https://oauth.net/2/grant-types/client-credentials/">\n    client_credentials</a> (for server-to-server communication)</li>\n    </ul>\n\n    Legacy, not recommended\n    <ul>\n    <li><a href="https://oauth.net/2/grant-types/implicit/">implicit</a>\n    (not recommended, using access_token in URL)</li>\n    <li>password (not recommended, using username and password)</li>\n    </ul>\n\n    ',
                    ),
                ),
                (
                    "client_id",
                    models.CharField(db_index=True, max_length=48, unique=True),
                ),
                ("client_secret", models.CharField(blank=True, max_length=48)),
                ("redirect_uris", models.TextField(blank=True, default="")),
                ("default_redirect_uri", models.TextField(blank=True, default="")),
                ("scope", models.TextField(default="")),
                (
                    "token_endpoint_auth_method",
                    models.CharField(
                        choices=[
                            ("client_secret_basic", "client_secret_basic"),
                            ("client_secret_post", "client_secret_post"),
                            ("client_secret_jwt", "client_secret_jwt"),
                            ("private_key_jwt", "private_key_jwt"),
                        ],
                        default="",
                        help_text='\n* client_secret_basic uses the HTTP Basic Authentication Scheme\nto authenticate.<br>\n<br>\n* client_secret_post uses the HTTP POST parameters to authenticate.<br>\n<br>\n* client_secret_jwt uses the JSON Web Token (JWT) to authenticate.\nCompared to client_secret_basic and client_secret_post, client_secret_jwt\ndoesn`t require sending the actual secret over the network.\nThis makes it more secure.<br>\n<br>\n* <a href="https://oauth.net/private-key-jwt/">private_key_jwt</a> uses\nthe JSON Web Token (JWT) to authenticate. Compared to client_secret_jwt,\nprivate_key_jwt uses a private key to sign the JWT. This makes it more secure.<br>\n',
                        max_length=120,
                    ),
                ),
                (
                    "response_type",
                    models.TextField(
                        default="",
                        help_text="\nValid options, array of space terminated:<br>\n{'code id_token', 'code token', 'code id_token token'} (hybrid)<br>\n{'id_token token', 'id_token'} (implicit)<br>\n{'code'} (authorization code)<br>\n",
                    ),
                ),
                ("require_nonce", models.BooleanField(default=False)),
                (
                    "require_code_challenge",
                    models.BooleanField(
                        default=False,
                        help_text='\nPKCE (Proof Key for Code Exchange) is a security feature that prevents an attacker\nfrom stealing an authorization code and using it to gain access to a user\'s account.\nSee <a href="https://tools.ietf.org/html/rfc7636">RFC 7636</a> for more information.\n',
                        verbose_name="Require PKCE",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.tenant",
                    ),
                ),
            ],
            options={
                "verbose_name": "OAuth2 Client",
                "verbose_name_plural": "OAuth2 Clients",
            },
            bases=(models.Model, authlib.oauth2.rfc6749.models.ClientMixin),
        ),
        migrations.CreateModel(
            name="AuthorizationCode",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("client_id", models.CharField(db_index=True, max_length=48)),
                ("code", models.CharField(max_length=120, unique=True)),
                ("redirect_uri", models.TextField(default="", null=True)),
                ("response_type", models.TextField(default="")),
                ("scope", models.TextField(default="", null=True)),
                (
                    "auth_time",
                    models.IntegerField(default=sso2.core.timeutils.now_timestamp),
                ),
                ("nonce", models.CharField(default="", max_length=120, null=True)),
                ("code_challenge", models.TextField(default="", null=True)),
                ("code_challenge_method", models.TextField(default="", null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "OAuth2 Authorization Code",
                "verbose_name_plural": "OAuth2 Authorization Codes",
            },
            bases=(models.Model, authlib.oauth2.rfc6749.models.AuthorizationCodeMixin),
        ),
    ]
    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations),
    ]