# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.urls import path

from . import views

urlpatterns = [
    path("", views.datarequest, name="datarequest"),
    path("download", views.datarequest_download, name="datarequest_download"),
]
