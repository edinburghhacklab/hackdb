# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from allauth.account.decorators import verified_email_required
from allauth.account.models import EmailAddress
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.urls import reverse
from django.views.decorators.http import require_POST

from . import mailmanapi
from .models import GroupPolicy, MailingList
from .utils import (
    audit_list,
    load_lists,
    user_can_see,
    user_can_subscribe,
    user_recommend,
)


class AddressChangeForm(forms.Form):
    list_name = forms.HiddenInput()
    email = forms.ChoiceField(choices=())

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        verified_addresses = EmailAddress.objects.filter(
            user=user, verified=True
        ).order_by("-primary")
        self.fields["email"].choices = [("", "(unsubscribe)")] + [
            (address.email, address.email) for address in verified_addresses
        ]


@login_required
@verified_email_required
def overview(request):
    verified_addresses = EmailAddress.objects.filter(
        user=request.user, verified=True
    ).order_by("-primary")

    try:
        subscriber_data = {}
        for address in verified_addresses:
            data = mailmanapi.get_member(address.email)
            if data is not None:
                subscriber_data[address.email] = data
            else:
                raise RuntimeError(f"No data returned for {address.email}")
    except Exception as e:
        context = {
            "error": "There was an error communicating with the Mailman server. Please try again later."
        }
        return render(request, "mailman2/error.html", context)

    context = {
        "verified_addresses": verified_addresses,
        "verified_address": verified_addresses[0],
        "mailman_url": settings.MAILMAN_URL,
        "mailinglists": [],
        "advanced_mode": True,
    }

    mailinglists = []
    for mailing_list in MailingList.objects.all():
        list_data = {
            # "obj": mailing_list,
            "name": mailing_list.name,
            "description": mailing_list.description,
            "archive_private": mailing_list.archive_private,
            "visible": False,
            "subscribed": False,
            "recommended": False,
            "subscriptions": [],
        }
        row = 0
        for address in verified_addresses:
            if user_can_see(request.user, mailing_list):
                list_data["visible"] = True
            if user_recommend(request.user, mailing_list):
                list_data["visible"] = True
                list_data["recommended"] = True
            if mailing_list.name in subscriber_data[address.email]:
                list_data["visible"] = True
                list_data["subscribed"] = True
                subscription = subscriber_data[address.email][mailing_list.name]
                subscription["row"] = row
                # subscription["obj"] = address
                subscription["email"] = address.email
                subscription["address_change_form"] = AddressChangeForm(
                    {"email": address.email, "list_name": mailing_list.name},
                    user=request.user,
                )
                list_data["subscriptions"].append(subscription)
                row = row + 1
        list_data["subscriptions_count"] = len(list_data["subscriptions"])
        if list_data["visible"]:
            mailinglists.append(list_data)

    context["mailinglists"] = mailinglists

    return render(request, "mailman2/overview.html", context)


@login_required
@verified_email_required
@require_POST
def subscribe(request, name, email=None):
    mailing_list = MailingList.objects.get(name=name)
    if email:
        verified_address = EmailAddress.objects.get(
            user=request.user, verified=True, email=email
        )
    else:
        verified_address = EmailAddress.objects.filter(
            user=request.user, verified=True
        ).first()
        if not verified_address:
            raise RuntimeError
    if user_can_subscribe(request.user, mailing_list):
        if settings.MAILMAN_ENABLE_INTERACTIVE_CHANGES:
            if mailmanapi.subscribe(name, verified_address.email):
                messages.add_message(
                    request, messages.SUCCESS, f"Subscribed to {name}."
                )
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"Error subscribing to {name}, please try again later.",
                )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                "Subscribes and unsubscribes are disabled at the moment.",
            )
    else:
        messages.add_message(
            request,
            messages.ERROR,
            f"Sorry, you are not authorised to subscribe to {name}.",
        )
    return HttpResponseRedirect(reverse("mailman2_overview"))


@login_required
@verified_email_required
@require_POST
def unsubscribe(request, name, email):
    verified_address = EmailAddress.objects.get(
        user=request.user, verified=True, email=email
    )
    if settings.MAILMAN_ENABLE_INTERACTIVE_CHANGES:
        if mailmanapi.unsubscribe(name, verified_address.email):
            messages.add_message(
                request, messages.SUCCESS, f"Unsubscribed from {name}."
            )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                f"Error unsubscribing from {name}, please try again later.",
            )
    else:
        messages.add_message(
            request,
            messages.ERROR,
            "Subscribes and unsubscribes are disabled at the moment.",
        )
    return HttpResponseRedirect(reverse("mailman2_overview"))


@login_required
@permission_required("mailman2.audit_lists", raise_exception=True)
def audit(request, name):
    load_lists()
    mailing_list = MailingList.objects.get(name=name)
    subscribers = audit_list(mailing_list)

    return render(
        request,
        "mailman2/audit.html",
        {
            "mailing_list": mailing_list,
            "subscribers": subscribers.values(),
            "policies": GroupPolicy.objects.filter(mailing_list=mailing_list).order_by(
                "group__name"
            ),
        },
    )
