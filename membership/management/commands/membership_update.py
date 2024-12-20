# SPDX-FileCopyrightText: 2022-2024 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.core.management.base import BaseCommand

from membership.models import Member


class Command(BaseCommand):
    help = "Update the membership status and members group"

    def handle(self, *args, **options):
        Member.fixup_all()
