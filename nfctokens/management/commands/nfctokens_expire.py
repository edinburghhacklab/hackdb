# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from nfctokens.models import NFCToken, NFCTokenLog


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        if settings.NFCTOKENS_LOG_RETENTION_DAYS:
            delete_before_date = timezone.make_aware(
                datetime.datetime.now()
            ) - datetime.timedelta(days=settings.NFCTOKENS_LOG_RETENTION_DAYS)
            NFCTokenLog.objects.filter(timestamp__lt=delete_before_date).delete()
            NFCToken.objects.filter(
                user=None, last_seen__lt=delete_before_date
            ).delete()
