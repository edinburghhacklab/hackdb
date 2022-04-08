# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import allauth.account.signals
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import MailmanUser
from .utils import global_change_address


@receiver(allauth.account.signals.email_changed)
def email_changed(request, user, from_email_address, to_email_address, **kwargs):
    try:
        user.mailmanuser
    except ObjectDoesNotExist:
        user.mailmanuser = MailmanUser.objects.create(user=user)

    if user.mailmanuser.advanced_mode:
        overview_url = reverse("mailman2_overview")
        messages.add_message(
            request,
            messages.WARNING,
            mark_safe(
                f"You may wish to <a href='{overview_url}'>update</a> your mailing list subscriptions."
            ),
        )
        return
    global_change_address(user, from_email_address.email, to_email_address.email)


@receiver(allauth.account.signals.email_removed)
def email_removed(request, user, email_address, **kwargs):
    # The user has removed an address.
    # Pick a replacement address (primary first, or whatever we can find)
    new_address = (
        user.emailaddress_set.filter(verified=True).order_by("-primary").first()
    )
    if new_address:
        global_change_address(user, email_address, new_address.email)
