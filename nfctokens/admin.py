# SPDX-FileCopyrightText: 2022-2023 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import datetime

from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import NFCToken, NFCTokenLog


class RecentDaysListFilter(admin.SimpleListFilter):
    title = "day"
    parameter_name = "day"

    def lookups(self, request, model_admin):
        today = datetime.date.today()
        return (
            (0, "Today"),
            (1, "Yesterday"),
            (2, (today - datetime.timedelta(days=2)).strftime("%a %d %b")),
            (3, (today - datetime.timedelta(days=3)).strftime("%a %d %b")),
            (4, (today - datetime.timedelta(days=4)).strftime("%a %d %b")),
            (5, (today - datetime.timedelta(days=5)).strftime("%a %d %b")),
            (6, (today - datetime.timedelta(days=6)).strftime("%a %d %b")),
            (7, (today - datetime.timedelta(days=7)).strftime("%a %d %b")),
        )

    def queryset(self, request, queryset):
        if self.value() is not None:
            today = datetime.date.today()
            start = today - datetime.timedelta(days=int(self.value()))
            end = today - datetime.timedelta(days=int(self.value()) - 1)
            return queryset.filter(timestamp__gte=start, timestamp__lt=end)


@admin.register(NFCToken)
class NFCTokenAdmin(admin.ModelAdmin):
    list_display = (
        "uid",
        "description",
        "name",
        "user",
        "enabled",
        "last_edit",
        "last_seen",
        "last_location",
    )
    list_display_links = ("uid",)
    ordering = (
        "user",
        "-last_seen",
    )
    search_fields = (
        "uid",
        "last_location",
        "user__username",
        "user__first_name",
        "user__last_name",
    )

    def name(self, obj):
        if obj.user:
            return obj.user.get_full_name()


@admin.register(NFCTokenLog)
class NFCTokenLogAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "ltype",
        "token_link",
        "location",
        "user_link",
        "token_description",
        "authorized",
    )
    list_display_links = None
    list_filter = ("location", "authorized", "ltype", RecentDaysListFilter)
    actions = None
    ordering = ("-timestamp",)
    search_fields = (
        "uid",
        "location",
        "name",
        "username",
        "token_description",
        "user__username",
        "user__first_name",
        "user__last_name",
    )

    def token_link(self, obj):
        if obj.token:
            return mark_safe(
                '<a href="{}">{}</a>'.format(
                    reverse("admin:nfctokens_nfctoken_change", args=(obj.token.pk,)),
                    obj.uid,
                )
            )
        else:
            return obj.uid

    token_link.short_description = "uid"

    def user_link(self, obj):
        if obj.user:
            return mark_safe(
                '<a href="{}">{}</a>'.format(
                    reverse("admin:auth_user_change", args=(obj.user.pk,)),
                    obj.name or obj.username,
                )
            )
        else:
            return obj.name or obj.username

    user_link.short_description = "user"


class NFCTokenInline(admin.TabularInline):
    model = NFCToken
    fields = ("uid", "description", "last_seen", "last_location", "enabled")
    readonly_fields = ("last_seen", "last_location")
    extra = 0
