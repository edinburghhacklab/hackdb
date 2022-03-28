# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.urls import path

from . import views

urlpatterns = [
    path("", views.overview, name="membership_overview"),
    path("myprofile", views.myprofile, name="myprofile"),
    path("register", views.show_register, name="show_register"),
]
