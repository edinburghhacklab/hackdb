# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Display assigned permissions for all users and groups"

    def handle(self, *args, **options):
        for group in Group.objects.order_by("name"):
            output = []
            for permission in group.permissions.all():
                output.append(str(permission))
            if output:
                print(f"group {group.name}")
                for line in output:
                    print(f"- {line}")
                print()

        for user in get_user_model().objects.order_by("username"):
            output = []
            if user.is_superuser:
                output.append("is_superuser")
            if user.is_staff:
                output.append("is_staff")
            for permission in user.user_permissions.all():
                output.append(str(permission))
            if output:
                print(f"user {user.username}")
                for line in output:
                    print(f"- {line}")
                print()
