# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.core.management.base import BaseCommand
from mailman2 import mailmanapi
from mailman2.models import MailingList
from django.conf import settings

from mailman2.utils import audit_list, load_lists


class Command(BaseCommand):
    help = "Audit mailing lists and issue unsubscribes"

    def add_arguments(self, parser):
        parser.add_argument("--list", nargs=1)
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Push required changes to Mailman API",
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Only report entries that require action to fix",
        )

    def handle(self, *args, **options):
        load_lists()

        if options["list"]:
            mailing_lists = [MailingList.objects.get(name=options["list"][0])]
        else:
            mailing_lists = MailingList.objects.all()

        for mailing_list in mailing_lists:

            if options["verbosity"] >= 2:
                print(f"--- {mailing_list.name} ---")

            for subscriber in audit_list(mailing_list).values():

                if options["verbosity"] >= 2:
                    print(subscriber)

                if subscriber.get("action") == "subscribe":
                    if options["verbosity"] >= 1:
                        print(f"{mailing_list.name}: subscribe {subscriber['address']}")
                    if options["fix"]:
                        if settings.MAILMAN_ENABLE_AUTO_SUBSCRIBE:
                            mailmanapi.subscribe(
                                mailing_list.name, subscriber["address"]
                            )
                        else:
                            print(f"MAILMAN_ENABLE_AUTO_SUBSCRIBE is disabled")
                elif subscriber.get("action") == "unsubscribe":
                    if options["verbosity"] >= 1:
                        print(
                            f"{mailing_list.name}: unsubscribe {subscriber['address']}"
                        )
                    if options["fix"]:
                        if settings.MAILMAN_ENABLE_AUTO_UNSUBSCRIBE:
                            mailmanapi.unsubscribe(
                                mailing_list.name, subscriber["address"]
                            )
                        else:
                            print(f"MAILMAN_ENABLE_AUTO_UNSUBSCRIBE is disabled")
