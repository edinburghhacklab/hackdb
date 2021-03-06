# Generated by Django 4.0.3 on 2022-03-26 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MOTD",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start", models.DateTimeField()),
                ("end", models.DateTimeField(blank=True, null=True)),
                ("message", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Message of the day",
                "verbose_name_plural": "Messages of the day",
            },
        ),
    ]
