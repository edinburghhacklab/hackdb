# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib import admin

from .models import MOTD


@admin.register(MOTD)
class MOTDAdmin(admin.ModelAdmin):
    list_display = ("start", "end", "message", "is_active")
