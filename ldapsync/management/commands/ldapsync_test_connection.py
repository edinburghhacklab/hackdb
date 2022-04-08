# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.core.management.base import BaseCommand

from ldapsync.utils import ldap_connection


class Command(BaseCommand):
    help = "Test the connection to the LDAP server"

    def handle(self, *args, **options):
        connection = ldap_connection()
        if connection:
            print("OK")
            if connection.tls_started:
                print("Using TLS")
            if connection.user:
                print(f"Connected as {connection.user}")
