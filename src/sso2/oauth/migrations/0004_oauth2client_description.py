# Generated by Django 4.2 on 2023-05-29 07:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("oauth", "0003_oauth2clientcredential"),
    ]

    operations = [
        migrations.AddField(
            model_name="oauth2client",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
    ]
