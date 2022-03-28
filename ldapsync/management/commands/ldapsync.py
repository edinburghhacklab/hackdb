# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from ldapsync.utils import (
    user_entry,
    group_entry,
    LDAP,
    normalise_entry,
    posix_group_entry,
)


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):

        server = LDAP()

        for user in get_user_model().objects.all():
            dn, entry = user_entry(user)
            server.sync_entry(dn, normalise_entry(entry))

        for group in Group.objects.all():
            dn, entry = group_entry(group)
            server.sync_entry(dn, normalise_entry(entry))

        for group in Group.objects.filter(posix__isnull=False):
            dn, entry = posix_group_entry(group)
            server.sync_entry(dn, normalise_entry(entry))
