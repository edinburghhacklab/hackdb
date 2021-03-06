# Generated by Django 4.0.3 on 2022-03-27 23:22

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import posixusers.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SSHKey",
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
                ("key", models.TextField()),
                ("comment", models.CharField(blank=True, max_length=255)),
                ("enabled", models.BooleanField(default=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "SSH key",
            },
        ),
        migrations.CreateModel(
            name="PosixUser",
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
                (
                    "uid",
                    models.PositiveBigIntegerField(
                        default=posixusers.models.default_uid,
                        unique=True,
                        validators=[
                            django.core.validators.MinValueValidator(1000),
                            django.core.validators.MaxValueValidator(4294967295),
                        ],
                    ),
                ),
                (
                    "shell",
                    models.CharField(blank=True, default="/bin/bash", max_length=255),
                ),
                ("password", models.CharField(blank=True, max_length=255)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="posix",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "POSIX user",
            },
        ),
        migrations.CreateModel(
            name="PosixGroup",
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
                (
                    "gid",
                    models.PositiveIntegerField(
                        default=posixusers.models.default_gid,
                        unique=True,
                        validators=[
                            django.core.validators.MinValueValidator(1000),
                            django.core.validators.MaxValueValidator(4294967295),
                        ],
                    ),
                ),
                (
                    "group",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="posix",
                        to="auth.group",
                    ),
                ),
            ],
            options={
                "verbose_name": "POSIX group",
            },
        ),
    ]
