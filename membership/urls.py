# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.urls import path

from . import views

urlpatterns = [
    path("", views.overview, name="membership_overview"),
    path("myprofile", views.myprofile, name="myprofile"),
    path("register", views.show_register, name="show_register"),
    path("api/member_count", views.member_count, name="member_count"),
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
