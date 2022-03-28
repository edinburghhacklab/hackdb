# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib import admin

from .models import DiscordUser, DiscordVerificationToken


class DiscordUserAdmin(admin.ModelAdmin):
    model = DiscordUser
    list_display = ("user", "discord_id", "discord_username")
    list_display_links = ("discord_id",)


admin.site.register(DiscordUser, DiscordUserAdmin)


class DiscordUserInline(admin.StackedInline):
    model = DiscordUser


class DiscordVerificationTokenAdmin(admin.ModelAdmin):
    model = DiscordVerificationToken
    list_display = ("created", "user", "discord_id", "discord_username")
    list_display_links = ("discord_id",)


admin.site.register(DiscordVerificationToken, DiscordVerificationTokenAdmin)
