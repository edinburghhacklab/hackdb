# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib import admin

from .models import ChangeOfAddress, GroupPolicy, MailingList


class GroupPolicyInline(admin.TabularInline):
    model = GroupPolicy
    fields = ("group", "policy", "prompt")
    extra = 0


def groups(obj):
    return [policy.group.name for policy in obj.group_policies.order_by("group__name")]


groups.short_description = "Groups"


@admin.register(MailingList)
class MailingListAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "advertised",
        "subscribe_policy",
        groups,
        "auto_unsubscribe",
    )
    ordering = ("name",)
    readonly_fields = (
        "name",
        "description",
        "info",
        "advertised",
        "subscribe_policy",
        "archive_private",
        "subscribe_auto_approval",
    )
    inlines = (GroupPolicyInline,)


@admin.register(ChangeOfAddress)
class ChangeOfAddressAdmin(admin.ModelAdmin):
    list_display = ("created", "user", "old_email", "new_email")
    ordering = ("created",)
    readonly_fields = ("created", "user", "old_email", "new_email")
