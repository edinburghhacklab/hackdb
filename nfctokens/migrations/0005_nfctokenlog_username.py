# Generated by Django 4.0.3 on 2022-04-07 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("nfctokens", "0004_alter_nfctoken_uid"),
    ]

    operations = [
        migrations.AddField(
            model_name="nfctokenlog",
            name="username",
            field=models.CharField(blank=True, editable=False, max_length=255),
        ),
    ]
