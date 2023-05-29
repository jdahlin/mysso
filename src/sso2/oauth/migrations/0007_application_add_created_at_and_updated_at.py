# Generated by Django 4.2 on 2023-05-29 12:26

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "oauth",
            "0006_rename_default_redirect_uri_oauth2client_allowed_callback_uris_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="oauth2client",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="oauth2client",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
