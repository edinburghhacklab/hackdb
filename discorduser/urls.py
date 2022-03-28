# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.urls import path

from . import views

urlpatterns = [
    path("api/users", views.api_get_users, name="discorduser_api_get_users"),
    path(
        "api/users/<int:discord_id>",
        views.api_get_user,
        name="discorduser_api_get_user",
    ),
    path(
        "api/generate_token",
        views.api_generate_token,
        name="discorduser_api_generate_token",
    ),
    path(
        "verify/<str:token>",
        views.verify_token,
        name="discorduser_verify_token",
    ),
]
