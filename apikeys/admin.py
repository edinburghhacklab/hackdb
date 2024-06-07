# SPDX-FileCopyrightText: 2022-2024 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib import admin

from .models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("uuid", "description", "enabled", "expires")
    list_display_links = ("uuid",)
