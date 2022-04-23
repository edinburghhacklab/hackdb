# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import datetime

import tabulate

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Per-user report of NFC Token assignment and usage"

    def add_arguments(self, parser):
        parser.add_argument("--reverse", action="store_true")
        parser.add_argument("--sort", type=str, nargs=1)

    def handle(self, *args, **options):
        last_1year = timezone.now() - datetime.timedelta(days=365)
        last_90d = timezone.now() - datetime.timedelta(days=90)
        last_30d = timezone.now() - datetime.timedelta(days=30)

        headers = [
            "Username",
            "Name",
            "Tokens",
            "Enabled",
            "1-year",
            "90-days",
            "30-days",
        ]
        output = []

        for user in get_user_model().objects.all():
            output.append(
                [
                    user.username,
                    user.get_full_name(),
                    user.nfctokens.count(),
                    user.nfctokens.filter(enabled=True).count(),
                    user.nfctokens.filter(
                        enabled=True, last_seen__gt=last_1year
                    ).count(),
                    user.nfctokens.filter(enabled=True, last_seen__gt=last_90d).count(),
                    user.nfctokens.filter(enabled=True, last_seen__gt=last_30d).count(),
                ]
            )

        try:
            sort_column = headers.index(options["sort"][0])
        except ValueError:
            sort_column = 0
        output.sort(key=lambda row: row[sort_column], reverse=options["reverse"])

        print(tabulate.tabulate(output, headers=headers))
