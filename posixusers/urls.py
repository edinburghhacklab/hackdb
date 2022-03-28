# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.urls import path

from . import views

urlpatterns = [
    path("", views.mysshkeys, name="posixusers_sshkeys"),
    path("add", views.mysshkeys_add, name="posixusers_sshkeys_add"),
    path("enable/<int:pk>", views.mysshkeys_enable, name="posixusers_sshkeys_enable"),
    path(
        "disable/<int:pk>", views.mysshkeys_disable, name="posixusers_sshkeys_disable"
    ),
    path("edit/<int:pk>", views.mysshkeys_edit, name="posixusers_sshkeys_edit"),
    path("delete/<int:pk>", views.mysshkeys_delete, name="posixusers_sshkeys_delete"),
]
