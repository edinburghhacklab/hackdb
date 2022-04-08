# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from allauth.account.decorators import verified_email_required
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST

from . import mailmanapi
from .models import GroupPolicy, MailingList, MailmanUser
from .utils import audit_list, auto_load_lists, load_lists


def build_overview_context(user):
    auto_load_lists()

    verified_addresses = EmailAddress.objects.filter(user=user, verified=True).order_by(
        "-primary"
    )

    try:
        MailmanUser.objects.get(user=user)
    except MailmanUser.DoesNotExist:
        MailmanUser.objects.create(user=user)

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
        return context

    used_addresses = {}

    context = {
        "verified_addresses": verified_addresses,
        "verified_address": verified_addresses[0],
        "mailman_url": settings.MAILMAN_URL,
        "mailinglists": [],
        "advanced_mode": user.mailmanuser.advanced_mode,
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
            "can_subscribe": False,
            "subscriptions": [],
        }
        row = 0
        for address in verified_addresses:
            group_policy = mailing_list.user_subscribe_policy(user)
            if mailing_list.advertised:
                list_data["visible"] = True
            if group_policy:
                if group_policy.policy >= GroupPolicy.ALLOW:
                    list_data["visible"] = True
                    list_data["can_subscribe"] = True
                if group_policy.policy >= GroupPolicy.RECOMMEND:
                    list_data["recommended"] = True
            if mailing_list.name in subscriber_data[address.email]:
                list_data["visible"] = True
                list_data["subscribed"] = True
                subscription = subscriber_data[address.email][mailing_list.name]
                subscription["row"] = row
                # subscription["obj"] = address
                subscription["email"] = address.email
                used_addresses[address.email] = True
                list_data["subscriptions"].append(subscription)
                row = row + 1
        list_data["subscriptions_count"] = len(list_data["subscriptions"])
        if list_data["visible"]:
            mailinglists.append(list_data)

    context["mailinglists"] = mailinglists

    if used_addresses == {}:
        pass
    elif list(used_addresses.keys()) == [verified_addresses[0].email]:
        pass
    else:
        context["advanced_mode"] = True

    return context


@login_required
@verified_email_required
def overview(request):
    context = build_overview_context(request.user)
    if "error" in context:
        return render(request, "mailman2/error.html", context)
    if context["advanced_mode"]:
        return render(request, "mailman2/overview_advanced.html", context)
    else:
        return render(request, "mailman2/overview_simple.html", context)


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
            user=request.user, primary=True, verified=True
        ).first()
        if not verified_address:
            raise RuntimeError
    if mailing_list.user_can_subscribe(request.user):
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
                "Subscription changes are disabled at the moment.",
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
            "Subscription changes are disabled at the moment.",
        )
    return HttpResponseRedirect(reverse("mailman2_overview"))


@login_required
@verified_email_required
@require_POST
def change_address(request, name, old_email, new_email):
    old_verified_address = EmailAddress.objects.get(
        user=request.user, verified=True, email=old_email
    )
    new_verified_address = EmailAddress.objects.get(
        user=request.user, verified=True, email=new_email
    )
    if settings.MAILMAN_ENABLE_INTERACTIVE_CHANGES:
        if mailmanapi.change_address(
            name, old_verified_address.email, new_verified_address.email
        ):
            messages.add_message(
                request, messages.SUCCESS, f"Changed address for {name}."
            )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                f"Error changing address for {name}, please try again later.",
            )
    else:
        messages.add_message(
            request,
            messages.ERROR,
            "Subscription changes are disabled at the moment.",
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


@login_required
@verified_email_required
@require_POST
def simple_mode(request):
    verified_addresses = EmailAddress.objects.filter(
        user=request.user, verified=True
    ).order_by("-primary")
    primary_address = verified_addresses[0]

    errors = False

    if settings.MAILMAN_ENABLE_INTERACTIVE_CHANGES:
        for address in verified_addresses:
            if address == primary_address:
                continue
            if not mailmanapi.global_change_address(
                address.email, primary_address.email
            ):
                errors = True
    else:
        messages.add_message(
            request,
            messages.ERROR,
            "Subscription changes are disabled at the moment.",
        )

    if not errors:
        try:
            mailmanuser = MailmanUser.objects.get(user=request.user)
        except MailmanUser.DoesNotExist:
            mailmanuser = MailmanUser.objects.create(user=request.user)
        mailmanuser.advanced_mode = False
        mailmanuser.save()

    return HttpResponseRedirect(reverse("mailman2_overview"))


@login_required
@verified_email_required
@require_POST
def advanced_mode(request):
    try:
        mailmanuser = MailmanUser.objects.get(user=request.user)
    except MailmanUser.DoesNotExist:
        mailmanuser = MailmanUser.objects.create(user=request.user)
    mailmanuser.advanced_mode = True
    mailmanuser.save()
    return HttpResponseRedirect(reverse("mailman2_overview"))
