# Generated by Django 4.2 on 2023-04-18 09:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0009_alter_oauth2client_client_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="oauth2client",
            name="response_type",
            field=models.TextField(
                default="",
                help_text="\nValid options, array of space terminated:<br>\n"
                "{'code id_token', 'code token', 'code id_token token'} "
                "(hybrid)<br>\n"
                "{'id_token token', 'id_token'} (implicit)<br>\n{'code'} "
                "(authorization code)<br>\n",
            ),
        ),
    ]