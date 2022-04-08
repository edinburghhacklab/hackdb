# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from ldapsync.serializers import serialize_group, serialize_posixgroup, serialize_user
from ldapsync.utils import LDAP


class Command(BaseCommand):
    help = "Perform a full sync to the LDAP server"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        if options["verbosity"] > 2:
            debug = True
        else:
            debug = False

        server = LDAP(dry_run=options["dry_run"], debug=debug)

        if settings.LDAPSYNC_USERS_BASE_DN:
            for user in get_user_model().objects.all():
                dn, entry = serialize_user(
                    user, settings.LDAPSYNC_USERS_BASE_DN, settings.LDAPSYNC_DOMAIN_SID
                )
                server.sync_entry(dn, entry)

            if settings.LDAPSYNC_GROUPS_BASE_DN:
                for group in Group.objects.all():
                    dn, entry = serialize_group(
                        group,
                        settings.LDAPSYNC_GROUPS_BASE_DN,
                        settings.LDAPSYNC_USERS_BASE_DN,
                    )
                    server.sync_entry(dn, entry)

        if settings.LDAPSYNC_POSIX_GROUPS_BASE_DN:
            for group in Group.objects.filter(posix__isnull=False):
                dn, entry = serialize_posixgroup(
                    group, settings.LDAPSYNC_POSIX_GROUPS_BASE_DN
                )
                server.sync_entry(dn, entry)

        if settings.LDAPSYNC_USERS_BASE_DN:
            server.auto_delete(settings.LDAPSYNC_USERS_BASE_DN)
            if settings.LDAPSYNC_GROUPS_BASE_DN:
                server.auto_delete(settings.LDAPSYNC_GROUPS_BASE_DN)
        if settings.LDAPSYNC_POSIX_GROUPS_BASE_DN:
            server.auto_delete(settings.LDAPSYNC_POSIX_GROUPS_BASE_DN)
