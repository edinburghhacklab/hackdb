# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib import admin

from .models import GroupOwnership, GroupProperties


@admin.register(GroupOwnership)
class GroupOwnershipAdmin(admin.ModelAdmin):
    model = GroupOwnership
    list_display = ("group", "user")
    list_display_links = ("user",)
    ordering = ("group", "user")


class GroupOwnershipInline(admin.TabularInline):
    model = GroupOwnership
    extra = 0


class GroupPropertiesInline(admin.TabularInline):
    model = GroupProperties
    extra = 1
