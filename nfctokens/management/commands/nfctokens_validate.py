# SPDX-FileCopyrightText: 2024 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError

from ...models import NFCToken


class Command(BaseCommand):
    help = "Run validation checks on all NFC tokens"

    def handle(self, *args, **options):
        for token in NFCToken.objects.order_by("uid"):
            try:
                token.full_clean()
            except ValidationError as e:
                print(token, e)
