# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib import admin

from .models import Member, MembershipSponsor, MembershipTerm


class MembershipTermInline(admin.TabularInline):
    model = MembershipTerm
    extra = 0


@admin.register(MembershipTerm)
class MembershipTermAdmin(admin.ModelAdmin):
    list_display = ("user", "start", "end", "mtype")
    list_display_links = ("start",)
    ordering = (
        "user",
        "start",
    )


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("user", "real_name", "membership_status", "is_member")
    list_display_links = ("real_name",)
    readonly_fields = ("membership_status",)


class MemberInline(admin.StackedInline):
    model = Member
    can_delete = False


@admin.register(MembershipSponsor)
class MembershipSponsorAdmin(admin.ModelAdmin):
    list_display = ("date", "sponsor", "sponsee")
