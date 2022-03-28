# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.mytokens, name="mytokens"),
    path("claim", views.mytokens_claim, name="mytokens_claim"),
    path("add", views.mytokens_add, name="mytokens_add"),
    re_path(
        r"^add/(?P<uid>[0-9a-fA-F]+)$", views.mytokens_add, name="mytokens_add_uid"
    ),
    re_path(
        r"^enable/(?P<uid>[0-9a-fA-F]+)$", views.mytokens_enable, name="mytokens_enable"
    ),
    re_path(
        r"^disable/(?P<uid>[0-9a-fA-F]+)$",
        views.mytokens_disable,
        name="mytokens_disable",
    ),
    re_path(r"^edit/(?P<uid>[0-9a-fA-F]+)$", views.mytokens_edit, name="mytokens_edit"),
    re_path(
        r"^delete/(?P<uid>[0-9a-fA-F]+)$", views.mytokens_delete, name="mytokens_delete"
    ),
    path("logs", views.mytokenlogs, name="mytokenlogs"),
    path("api/nfc_tokens", views.nfc_tokens, name="nfc_tokens"),
    path("api/nfc_token_auth", views.nfc_token_auth, name="nfc_token_auth"),
]
