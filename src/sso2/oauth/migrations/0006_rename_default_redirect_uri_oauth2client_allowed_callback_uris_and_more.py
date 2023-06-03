# Generated by Django 4.2 on 2023-05-29 11:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("oauth", "0005_remove_oauth2client_grant_type_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="oauth2client",
            old_name="default_redirect_uri",
            new_name="allowed_callback_uris",
        ),
        migrations.RemoveField(
            model_name="oauth2client",
            name="redirect_uris",
        ),
    ]