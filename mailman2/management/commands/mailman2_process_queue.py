# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.core.management.base import BaseCommand

from mailman2.utils import process_queue


class Command(BaseCommand):
    help = "Process changes that couldn't be handled in real time"

    def handle(self, *args, **options):
        for line in process_queue():
            print(line)
