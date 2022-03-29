# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.conf import settings
from django.contrib.auth import get_user_model

from . import mailmanapi
from .models import ChangeOfAddress, GroupPolicy, MailingList


def load_lists():
    seen = {}

    for list_name, list_data in mailmanapi.get_lists().items():
        try:
            l = MailingList.objects.get(name=list_name)
        except MailingList.DoesNotExist:
            l = MailingList(name=list_name)
        l.description = list_data["description"]
        l.info = list_data["info"]
        l.advertised = list_data["advertised"]
        l.subscribe_policy = list_data["subscribe_policy"]
        l.archive_private = list_data["archive_private"]
        l.subscribe_auto_approval = "\n".join(list_data["subscribe_auto_approval"])
        l.save()
        seen[list_name] = True

    for mailing_list in MailingList.objects.all():
        if mailing_list.name not in seen:
            mailing_list.delete()


def user_can_subscribe(user, mailing_list):
    if mailing_list.subscribe_policy in [MailingList.CONFIRM]:
        # print(f"user_can_subscribe({user}, {mailing_list}): yes, open list")
        return True
    if user:
        for group in user.groups.all():
            if GroupPolicy.objects.filter(
                group=group, mailing_list=mailing_list
            ).exists():
                # print(f"user_can_subscribe({user}, {mailing_list}): yes, in group {policy.group}")
                return True
    if mailing_list.check_subscribe_auto_approval(user.email):
        return True
    # print(f"user_can_subscribe({user}, {mailing_list}): no")
    return False


def user_can_see(user, mailing_list):
    if mailing_list.advertised:
        # print(f"user_can_see({user}, {mailing_list}): yes, advertised list")
        return True
    if user:
        for group in user.groups.all():
            if GroupPolicy.objects.filter(
                group=group, mailing_list=mailing_list
            ).exists():
                # print(f"user_can_see({user}, {mailing_list}): yes, in group {group}")
                return True
    if mailing_list.check_subscribe_auto_approval(user.email):
        return True
    # print(f"user_can_see({user}, {mailing_list}): no")
    return False


def user_recommend(user, mailing_list):
    if user:
        for group in user.groups.all():
            if GroupPolicy.objects.filter(
                group=group,
                mailing_list=mailing_list,
                policy__gte=GroupPolicy.RECOMMEND,
            ).exists():
                return True
    return False


def user_prompt(user, mailing_list):
    if user:
        for group in user.groups.all():
            try:
                return GroupPolicy.objects.get(
                    group=group, policy=GroupPolicy.PROMPT, mailing_list=mailing_list
                ).prompt
            except GroupPolicy.DoesNotExist:
                pass
    return None


def user_subscribe_policy(mailing_list, user):
    best = None
    for group in user.groups.all():
        for policy in GroupPolicy.objects.filter(
            group=group, mailing_list=mailing_list
        ):
            if best is None:
                best = policy
            else:
                if policy.policy > best.policy:
                    best = policy
    return best


def audit_list(mailing_list):
    mailman_subscribers = mailmanapi.get_list_members(mailing_list.name)

    subscribers = {}

    for user in get_user_model().objects.all():
        policy = user_subscribe_policy(mailing_list, user)
        if policy:
            user_is_subscribed = False
            verified_addresses = user.emailaddress_set.filter(verified=True).order_by(
                "-primary"
            )
            for address in verified_addresses:
                email = address.email.lower()
                # print(f"user_subscribe_policy {mailing_list} {user} -> {policy}")
                address_is_subscribed = email in mailman_subscribers
                subscribers[email] = {
                    "user": user,
                    "address": email,
                    "subscribed": address_is_subscribed,
                    "policy": policy,
                }
                if address_is_subscribed:
                    user_is_subscribed = True
            if (
                policy.policy == GroupPolicy.FORCE
                and not user_is_subscribed
                and len(verified_addresses) > 0
            ):
                subscribers[verified_addresses[0].email]["action"] = "subscribe"

    for address in mailman_subscribers:
        address = address.lower()
        if address in subscribers:
            continue
        subscribers[address] = {
            "address": address,
            "subscribed": True,
        }
        if mailing_list.auto_unsubscribe:
            if mailing_list.check_subscribe_auto_approval(address):
                subscribers[address]["auto_approval"] = True
            else:
                subscribers[address]["action"] = "unsubscribe"

    return subscribers


def change_address(user, old_address, new_address):
    if old_address:
        if settings.MAILMAN_ENABLE_ADDRESS_CHANGES:
            try:
                if mailmanapi.change_address(old_address, new_address):
                    return True
            except Exception as e:
                print("Exception while talking to Mailman API:", e)
            print("live change of address failed, queue for retry")
        else:
            print(
                "address changes disabled by MAILMAN_ENABLE_ADDRESS_CHANGES, queue for later"
            )
        change = ChangeOfAddress(
            user=user, old_email=old_address, new_email=new_address
        )
        change.save()


def process_queue():
    for change in ChangeOfAddress.objects.order_by("created"):
        if settings.MAILMAN_ENABLE_ADDRESS_CHANGES:
            if mailmanapi.change_address(change.old_email, change.new_email):
                change.delete()
                yield f"{change.old_email} -> {change.new_email}: ok"
            else:
                yield f"{change.old_email} -> {change.new_email}: not changed"
        else:
            yield f"{change.old_email} -> {change.new_email}: not changed, disabled by MAILMAN_ENABLE_ADDRESS_CHANGES"
