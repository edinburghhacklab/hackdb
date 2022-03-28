# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from ldapsync.utils import group_entry, posix_group_entry, user_entry


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):

        for user in get_user_model().objects.all():
            dn, entry = user_entry(user)
            print(dn, entry)

        for group in Group.objects.all():
            dn, entry = group_entry(group)
            print(dn, entry)

        for group in Group.objects.filter(posix__isnull=False):
            dn, entry = posix_group_entry(group)
            print(dn, entry)
