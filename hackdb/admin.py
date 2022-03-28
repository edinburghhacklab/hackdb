# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from allauth.account.models import EmailAddress
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from groupadmin.admin import GroupOwnershipInline, GroupPropertiesInline
from membership.admin import MemberInline, MembershipTermInline
from nfctokens.admin import NFCTokenInline
from posixusers.admin import PosixGroupInline, PosixUserInline, SSHKeyInline


class EmailAddressInline(admin.TabularInline):
    model = EmailAddress
    fields = ("email", "primary", "verified")
    readonly_fields = ("verified",)
    extra = 0


class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_member",
    )
    list_filter = ("member__membership_status",)
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "member__real_name",
    )
    inlines = (
        EmailAddressInline,
        MemberInline,
        MembershipTermInline,
        NFCTokenInline,
        PosixUserInline,
        SSHKeyInline,
    )

    def is_member(self, obj):
        try:
            return obj.member.is_member()
        except:
            return False

    is_member.boolean = True


class UserInline(admin.TabularInline):
    model = Group.user_set.through
    extra = 0


class CustomGroupAdmin(admin.ModelAdmin):
    model = Group
    inlines = (
        GroupPropertiesInline,
        PosixGroupInline,
        GroupOwnershipInline,
        UserInline,
    )
    ordering = ("name",)


admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)

admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), CustomUserAdmin)
