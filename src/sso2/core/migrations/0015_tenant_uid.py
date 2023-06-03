# Generated by Django 4.2 on 2023-05-20 22:22

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0014_alter_user_phone_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenant",
            name="uid",
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
    ]