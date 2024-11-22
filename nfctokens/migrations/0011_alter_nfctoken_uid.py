# Generated by Django 5.1.3 on 2024-11-22 22:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("nfctokens", "0010_alter_nfctoken_uid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="nfctoken",
            name="uid",
            field=models.CharField(
                max_length=32,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Enter a valid UID of 8, 14 or 20 hexadecimal digits",
                        regex="^([0-9a-f]{8}|[0-9a-f]{14}|[0-9a-f]{20})$",
                    ),
                    django.core.validators.RegexValidator(
                        inverse_match=True,
                        message="This is a randomly-generated UID which cannot be used for authentication",
                        regex="^08[0-9a-f]{6}$",
                    ),
                    django.core.validators.RegexValidator(
                        inverse_match=True,
                        message="This is a common fixed/non-unique UID which cannot be used for authentication",
                        regex="^(0{8}|0{14}|0{20}|f{8}|f{14}|f{20}|01020304|01020304050607|04ffffff|12345678)$",
                    ),
                    django.core.validators.RegexValidator(
                        inverse_match=True,
                        message="This is an invalid UID (contains a cascade tag)",
                        regex="^88[0-9a-f]{6}$",
                    ),
                    django.core.validators.RegexValidator(
                        inverse_match=True,
                        message="This is an invalid UID (contains a cascade tag)",
                        regex="^[0-9a-f]{6}88[0-9a-f]{6}$",
                    ),
                    django.core.validators.RegexValidator(
                        inverse_match=True,
                        message="This is an invalid UID (contains a cascade tag)",
                        regex="^[0-9a-f]{6}88[0-9a-f]{12}$",
                    ),
                ],
                verbose_name="UID",
            ),
        ),
    ]
