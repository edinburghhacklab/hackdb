# SPDX-FileCopyrightText: 2023 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.urls import path

from . import views

urlpatterns = [
    path("", views.groupadmin_list, name="groupadmin_list"),
    path("<str:group_name>", views.groupadmin_view, name="groupadmin_view"),
    path(
        "<str:group_name>/members/add",
        views.groupadmin_add_member,
        name="groupadmin_add_member",
    ),
    path(
        "<str:group_name>/members/remove/<int:user_id>",
        views.groupadmin_remove_member,
        name="groupadmin_remove_member",
    ),
    path(
        "<str:group_name>/owners/add",
        views.groupadmin_add_owner,
        name="groupadmin_add_owner",
    ),
    path(
        "<str:group_name>/owners/remove/<int:user_id>",
        views.groupadmin_remove_owner,
        name="groupadmin_remove_owner",
    ),
    path("<str:group_name>/join", views.groupadmin_join, name="groupadmin_join"),
    path("<str:group_name>/leave", views.groupadmin_leave, name="groupadmin_leave"),
]
