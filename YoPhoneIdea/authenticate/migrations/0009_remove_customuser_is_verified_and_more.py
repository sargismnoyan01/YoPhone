# Generated by Django 5.1.3 on 2025-02-27 14:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("authenticate", "0008_customuser_user_end_customuser_user_start"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="customuser",
            name="is_verified",
        ),
        migrations.RemoveField(
            model_name="customuser",
            name="user_end",
        ),
        migrations.RemoveField(
            model_name="customuser",
            name="user_start",
        ),
    ]
