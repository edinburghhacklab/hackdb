# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.urls import path

from . import views

urlpatterns = [
    path("", views.groupadmin_list, name="groupadmin_list"),
    path("<str:group_name>", views.groupadmin_view, name="groupadmin_view"),
    path("<str:group_name>/add", views.groupadmin_add_user, name="groupadmin_add_user"),
    path(
        "<str:group_name>/remove/<int:user_id>",
        views.groupadmin_remove_user,
        name="groupadmin_remove_user",
    ),
    path("<str:group_name>/join", views.groupadmin_join, name="groupadmin_join"),
    path("<str:group_name>/leave", views.groupadmin_leave, name="groupadmin_leave"),
]
