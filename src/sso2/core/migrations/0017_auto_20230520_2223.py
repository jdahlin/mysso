# Generated by Django 4.2 on 2023-05-20 22:23

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0016_auto_20230520_2223"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tenant",
            name="uid",
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
