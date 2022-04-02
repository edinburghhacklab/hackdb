# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.mytokens, name="nfctokens_mytokens"),
    path("claim", views.mytokens_claim, name="nfctokens_mytokens_claim"),
    path("add", views.mytokens_add, name="nfctokens_mytokens_add"),
    re_path(
        r"^add/(?P<uid>[0-9a-fA-F]+)$",
        views.mytokens_add,
        name="nfctokens_mytokens_add_uid",
    ),
    re_path(
        r"^enable/(?P<uid>[0-9a-fA-F]+)$",
        views.mytokens_enable,
        name="nfctokens_mytokens_enable",
    ),
    re_path(
        r"^disable/(?P<uid>[0-9a-fA-F]+)$",
        views.mytokens_disable,
        name="nfctokens_mytokens_disable",
    ),
    re_path(
        r"^edit/(?P<uid>[0-9a-fA-F]+)$",
        views.mytokens_edit,
        name="nfctokens_mytokens_edit",
    ),
    re_path(
        r"^delete/(?P<uid>[0-9a-fA-F]+)$",
        views.mytokens_delete,
        name="nfctokens_mytokens_delete",
    ),
    path("logs", views.mytokenlogs, name="nfctokens_mytokenlogs"),
    path("api/nfc_tokens", views.nfc_tokens, name="nfctokens_api_nfc_tokens"),
    path(
        "api/nfc_token_auth", views.nfc_token_auth, name="nfctokens_api_nfc_token_auth"
    ),
]
