# Generated by Django 4.2 on 2023-05-25 17:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0021_tenant_certificate_pem"),
        ("oauth", "0002_oauth2authorizedapp"),
    ]

    operations = [
        migrations.CreateModel(
            name="OAuth2ClientCredential",
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
                ("name", models.TextField()),
                ("pem_data", models.TextField()),
                ("thumbprint", models.TextField(default="")),
                (
                    "algorithm",
                    models.TextField(
                        choices=[
                            ("RS256", "RS256"),
                            ("RS384", "RS384"),
                            ("PS256", "PS256"),
                        ],
                        default="RS256",
                    ),
                ),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="public_keys",
                        to="oauth.oauth2client",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.tenant",
                    ),
                ),
            ],
        ),
    ]
