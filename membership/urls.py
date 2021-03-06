# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.urls import path

from . import views

urlpatterns = [
    path("", views.overview, name="membership_overview"),
    path("profile", views.profile, name="membership_profile"),
    path("register", views.show_register, name="membership_register"),
    path(
        "register_with_address",
        views.show_register_with_address,
        name="membership_register_with_address",
    ),
    path(
        "register_with_display_names",
        views.show_register_with_display_names,
        name="membership_register_with_display_names",
    ),
    path("api/member_count", views.member_count, name="membership_count"),
    path(
        "api/xero_contacts",
        views.xero_contacts_json,
        name="membership_xero_contacts_json",
    ),
    path(
        "api/xero_update_uuid",
        views.xero_update_uuid,
        name="membership_xero_update_uuid",
    ),
]
