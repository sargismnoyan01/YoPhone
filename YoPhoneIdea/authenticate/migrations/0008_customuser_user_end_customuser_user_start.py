# Generated by Django 5.1.3 on 2025-02-26 19:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authenticate", "0007_customuser_is_verified"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="user_end",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="customuser",
            name="user_start",
            field=models.IntegerField(default=0),
        ),
    ]
