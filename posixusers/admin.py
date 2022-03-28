# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib import admin

from .models import PosixGroup, PosixUser, SSHKey


@admin.register(PosixUser)
class PosixUserAdmin(admin.ModelAdmin):
    model = PosixUser
    list_display = ("user", "uid", "shell")
    list_display_links = ("uid",)
    ordering = ("uid",)


@admin.register(PosixGroup)
class PosixGroupAdmin(admin.ModelAdmin):
    model = PosixGroup
    list_display = ("group", "gid")
    list_display_links = ("gid",)
    ordering = ("gid",)


class PosixUserInline(admin.StackedInline):
    model = PosixUser
    extra = 0


class PosixGroupInline(admin.StackedInline):
    model = PosixGroup
    extra = 0


@admin.register(SSHKey)
class SSHKeyAdmin(admin.ModelAdmin):
    list_display = ("user", "comment", "truncated_key", "enabled")
    list_display_links = ("truncated_key",)

    @admin.display(description="key")
    def truncated_key(self, obj):
        value = obj.key
        if len(value) > 40:
            return value[0:37] + "..."
        else:
            return value


class SSHKeyInline(admin.TabularInline):
    model = SSHKey
    extra = 0
