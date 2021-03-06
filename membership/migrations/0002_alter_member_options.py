# Generated by Django 4.0.3 on 2022-04-02 12:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("membership", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="member",
            options={
                "permissions": [
                    ("view_register", "Can view the register of members"),
                    ("get_xero_contacts", "Can get contact data for Xero"),
                    ("update_xero_contacts", "Can update member Xero UUIDs"),
                ]
            },
        ),
    ]
