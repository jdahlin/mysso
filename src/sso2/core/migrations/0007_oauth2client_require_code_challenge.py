# Generated by Django 4.2 on 2023-04-15 14:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_oauth2client_require_nonce"),
    ]

    operations = [
        migrations.AddField(
            model_name="oauth2client",
            name="require_code_challenge",
            field=models.BooleanField(default=False),
        ),
    ]
