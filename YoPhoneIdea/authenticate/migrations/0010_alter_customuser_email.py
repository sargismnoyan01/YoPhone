# Generated by Django 5.1.3 on 2025-02-27 14:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authenticate", "0009_remove_customuser_is_verified_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="email",
            field=models.EmailField(
                max_length=254, unique=True, verbose_name="email address"
            ),
        ),
    ]
