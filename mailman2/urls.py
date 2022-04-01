# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.urls import path

from . import views

urlpatterns = [
    path("", views.overview, name="mailman2_overview"),
    path(
        "<str:name>/subscribe",
        views.subscribe,
        name="mailman2_subscribe_primary",
    ),
    path(
        "<str:name>/subscribe/<str:email>",
        views.subscribe,
        name="mailman2_subscribe",
    ),
    path(
        "<str:name>/unsubscribe/<str:email>",
        views.unsubscribe,
        name="mailman2_unsubscribe",
    ),
    path(
        "<str:name>/change_address/<str:old_email>/<str:new_email>",
        views.change_address,
        name="mailman2_change_address",
    ),
    path("<str:name>/audit", views.audit, name="mailman2_audit"),
    path("simple_mode", views.simple_mode, name="mailman2_simple_mode"),
    path("advanced_mode", views.advanced_mode, name="mailman2_advanced_mode"),
]
