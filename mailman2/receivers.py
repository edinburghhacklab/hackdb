# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import allauth.account.signals
from django.dispatch import receiver

from .utils import change_address

# FIXME: should we follow the primary address?
# how do we tell if the user wants all subscriptions the same
# or difference addresses per subscription?
#
# @receiver(allauth.account.signals.email_changed)
# def email_changed(request, user, from_email_address, to_email_address):
#     pass


@receiver(allauth.account.signals.email_removed)
def email_removed(request, user, email_address, **kwargs):
    # The user has removed an address.
    # Pick a replacement address (primary first, or whatever we can find)
    new_address = (
        user.emailaddress_set.filter(verified=True).order_by("-primary").first()
    )
    if new_address:
        change_address(user, email_address, new_address.email)
