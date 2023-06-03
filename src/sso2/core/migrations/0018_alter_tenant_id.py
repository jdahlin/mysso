# Generated by Django 4.2 on 2023-05-20 22:27

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0017_auto_20230520_2223"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tenant",
            name="id",
            field=models.UUIDField(
                auto_created=True,
                default=uuid.uuid4,
                editable=False,
                primary_key=True,
                serialize=False,
                verbose_name="ID",
            ),
        ),
    ]