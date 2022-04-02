# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path
from django.views.generic import TemplateView

import membership.views
import nfctokens.views

urlpatterns = [
    path(
        "", login_required(TemplateView.as_view(template_name="home.html")), name="home"
    ),
    path("accounts/", include("allauth.urls")),
    path("admin/", admin.site.urls),
    path("datarequest/", include("datarequest.urls")),
    path("discord/", include("discorduser.urls")),
    path("groups/", include("groupadmin.urls")),
    path("mailinglists/", include("mailman2.urls")),
    path("membership/", include("membership.urls")),
    path("nfctokens/", include("nfctokens.urls")),
    path("posix/", include("posixusers.urls")),
    # Legacy API paths
    path("api/1/member_stats", membership.views.member_count),
    path("api/1/nfc_token_auth", nfctokens.views.nfc_token_auth),
    path("api/1/nfc_tokens", nfctokens.views.nfc_tokens),
    path("api/1/xero_contacts", membership.views.xero_contacts_json),
    path("api/1/xero_update_uuid", membership.views.xero_update_uuid),
]
