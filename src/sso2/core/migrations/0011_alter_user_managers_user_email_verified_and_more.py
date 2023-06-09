# Generated by Django 4.2 on 2023-04-21 11:53

from django.db import migrations, models

import sso2.core.models.user_model


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_user_updated_at_alter_oauth2client_response_type"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="user",
            managers=[
                ("objects", sso2.core.models.user_model.CustomUserManager()),
            ],
        ),
        migrations.AddField(
            model_name="user",
            name="email_verified",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="oauth2client",
            name="grant_type",
            field=models.TextField(
                choices=[
                    ("authorization_code", "Authorization Code"),
                    ("client_credentials", "Client Credentials (server to server)"),
                    ("urn:ietf:params:oauth:grant-type:device_code", "Device code"),
                    ("implicit", "Implicit (legacy)"),
                    ("password", "Password (legacy)"),
                    ("refresh_token", "Refresh Token"),
                ],
                default="",
                help_text='\n    OAuth2/OpenID Connect grant types. Recommended grant types are:<br>\n    <ul>\n    <li><a href="https://oauth.net/2/grant-types/authorization-code/">\n    authorization_code</a> (optionally with\n    <a href="https://oauth.net/2/pkce/">PKCE</a>)</li>\n    <li><a href="https://oauth.net/2/grant-types/refresh-token/">\n    refresh_token</a></li>\n    <li><a href="https://oauth.net/2/grant-types/device-code/">\n    device code</a></li>\n    <li><a href="https://oauth.net/2/grant-types/client-credentials/">\n    client_credentials</a> (for server-to-server communication)</li>\n    </ul>\n\n    Legacy, not recommended\n    <ul>\n    <li><a href="https://oauth.net/2/grant-types/implicit/">implicit</a>\n    (not recommended, using access_token in URL)</li>\n    <li>password (not recommended, using username and password)</li>\n    </ul>\n\n    ',
            ),
        ),
        migrations.AlterField(
            model_name="oauth2client",
            name="require_code_challenge",
            field=models.BooleanField(
                default=False,
                help_text='\nPKCE (Proof Key for Code Exchange) is a security feature that prevents an attacker\nfrom stealing an authorization code and using it to gain access to a user\'s account.\nSee <a href="https://tools.ietf.org/html/rfc7636">RFC 7636</a> for more information.\n',
                verbose_name="Require PKCE",
            ),
        ),
        migrations.AlterField(
            model_name="oauth2client",
            name="token_endpoint_auth_method",
            field=models.CharField(
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
    ]
