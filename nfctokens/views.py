# SPDX-FileCopyrightText: 2022-2024 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.forms import ModelForm
from django.forms.widgets import TextInput
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST

from .models import NFCToken, NFCTokenLog


def too_many_enabled_tokens(user):
    enabled_count = user.nfctokens.filter(enabled=True).count()
    if enabled_count >= settings.NFCTOKENS_USER_ENABLED_LIMIT:
        return True


def too_many_tokens(user):
    total_count = user.nfctokens.filter().count()
    if total_count >= settings.NFCTOKENS_USER_TOTAL_LIMIT:
        return True


class TokenAddForm(ModelForm):
    class Meta:
        model = NFCToken
        fields = ["uid", "description"]


class TokenEditForm(ModelForm):
    class Meta:
        model = NFCToken
        fields = ["uid", "description"]
        widgets = {"uid": TextInput(attrs={"readonly": "true"})}

    def clean_uid(self):
        if self.cleaned_data["uid"] != self.instance.uid:
            # don't allow uid to be changed
            return self.instance.uid
        else:
            return self.cleaned_data["uid"]


@login_required
def mytokens(request):
    context = {
        "tokens": request.user.nfctokens.all(),
    }
    return render(request, "nfctokens/mytokens.html", context)


@login_required
@permission_required("nfctokens.self_configure_token", raise_exception=True)
def mytokens_add(request, uid=None):
    if too_many_tokens(request.user):
        messages.add_message(request, messages.ERROR, "Too many tokens.")
        return HttpResponseRedirect(reverse("nfctokens_mytokens"))
    if too_many_enabled_tokens(request.user):
        messages.add_message(request, messages.ERROR, "Too many enabled tokens.")
        return HttpResponseRedirect(reverse("nfctokens_mytokens"))
    if request.method == "POST":
        try:
            token = NFCToken.unassigned_objects.get(uid=uid)
            token.user = request.user
            token.description = ""
        except NFCToken.DoesNotExist:
            token = NFCToken(user=request.user)
        token.enabled = True
        token.last_edit = timezone.now()
        form = TokenAddForm(request.POST, instance=token)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Token added.")
            return HttpResponseRedirect(reverse("nfctokens_mytokens"))
    else:
        form = TokenAddForm(initial={"uid": uid})
        if uid is None:
            form.fields["uid"].help_text = (
                "The serial number or UID of your token. This may be read using an app on some Android phones."
            )
        form.fields["description"].help_text = (
            'This is to help you identify the token if you have more than one. For example, "blue keyfob".'
        )
    context = {"form": form}
    return render(request, "nfctokens/mytokens_add.html", context)


@login_required
@permission_required("nfctokens.self_configure_token", raise_exception=True)
def mytokens_edit(request, uid):
    token = request.user.nfctokens.get(uid=uid)
    if request.method == "POST":
        form = TokenEditForm(request.POST, instance=token)
        if form.is_valid():
            token.last_edit = timezone.now()
            form.save()
            messages.add_message(request, messages.SUCCESS, "Token updated.")
            return HttpResponseRedirect(reverse("nfctokens_mytokens"))
    else:
        form = TokenEditForm(instance=token)
    context = {"form": form}
    return render(request, "nfctokens/mytokens_edit.html", context)


@login_required
@permission_required("nfctokens.self_configure_token", raise_exception=True)
def mytokens_claim(request):
    if too_many_tokens(request.user):
        messages.add_message(request, messages.ERROR, "Too many tokens.")
        return HttpResponseRedirect(reverse("nfctokens_mytokens"))
    if too_many_enabled_tokens(request.user):
        messages.add_message(request, messages.ERROR, "Too many enabled tokens.")
        return HttpResponseRedirect(reverse("nfctokens_mytokens"))
    context = {"tokens": NFCToken.recent_objects.all()}
    return render(request, "nfctokens/mytokens_claim.html", context)


@login_required
@permission_required("nfctokens.self_configure_token", raise_exception=True)
def mytokens_delete(request, uid):
    token = request.user.nfctokens.get(uid=uid)
    if request.method == "POST":
        token.delete()
        messages.add_message(
            request, messages.SUCCESS, "Token %s deleted." % (token.uid)
        )
        return HttpResponseRedirect(reverse("nfctokens_mytokens"))
    else:
        return render(request, "nfctokens/mytokens_delete.html", {"token": token})


@login_required
@permission_required("nfctokens.self_configure_token", raise_exception=True)
@require_POST
def mytokens_enable(request, uid):
    if too_many_enabled_tokens(request.user):
        messages.add_message(request, messages.ERROR, "Too many enabled tokens.")
        return HttpResponseRedirect(reverse("nfctokens_mytokens"))
    token = request.user.nfctokens.get(uid=uid)
    token.enabled = True
    token.last_edit = timezone.now()
    token.save()
    messages.add_message(request, messages.SUCCESS, "Token %s enabled." % (token.uid))
    return HttpResponseRedirect(reverse("nfctokens_mytokens"))


@login_required
@permission_required("nfctokens.self_configure_token", raise_exception=True)
@require_POST
def mytokens_disable(request, uid):
    token = request.user.nfctokens.get(uid=uid)
    token.enabled = False
    token.last_edit = timezone.now()
    token.save()
    messages.add_message(request, messages.SUCCESS, "Token %s disabled." % (token.uid))
    return HttpResponseRedirect(reverse("nfctokens_mytokens"))


@login_required
@permission_required("nfctokens.self_view_tokenlog", raise_exception=True)
def mytokenlogs(request):
    context = {
        "tokens": request.user.nfctokenlogs.all().order_by("-timestamp"),
    }
    return render(request, "nfctokens/mytokenlogs.html", context)


def get_groups(user):
    return sorted(group.name for group in user.groups.all())


def token_sighting(token, location, authorized, type_="unknown", timestamp=None):
    if timestamp is None:
        timestamp = timezone.now()

    token.last_seen = timestamp
    token.last_location = location
    token.full_clean()
    token.save()

    tokenlog = NFCTokenLog()
    tokenlog.ltype = type_
    tokenlog.timestamp = timestamp
    tokenlog.uid = token.uid
    tokenlog.location = location or ""
    tokenlog.authorized = authorized
    tokenlog.token = token
    tokenlog.token_description = tokenlog.token.description
    tokenlog.user = tokenlog.token.user
    if tokenlog.user:
        tokenlog.username = tokenlog.user.username
        tokenlog.name = tokenlog.user.get_full_name()
    tokenlog.full_clean()
    tokenlog.save()


@require_GET
@permission_required("nfctokens.export_tokens", raise_exception=True)
def nfc_tokens(request):
    data = {}
    for user in get_user_model().objects.all().prefetch_related("groups", "nfctokens"):
        if not user.is_active:
            continue
        username = user.username or user.email
        groups = get_groups(user)
        tokens = []
        for token in user.nfctokens.filter(enabled=True):
            tokens.append(token.uid)
        if len(groups) > 0 and len(tokens) > 0:
            data[username] = {
                "groups": groups,
                "tokens": sorted(tokens),
            }
    return JsonResponse(data)


@never_cache
@require_POST
@permission_required("nfctokens.auth_token", raise_exception=True)
def nfc_token_auth(request):
    data = json.loads(request.body.decode())
    uid = data["uid"].strip().lower()
    location = data.get("location")
    required_groups = data.get("groups")
    exclude_groups = data.get("exclude_groups", [])

    if len(uid) == 8 and uid.startswith("08"):
        return JsonResponse(
            {"found": False, "authorized": False, "reason": "Random UID not allowed"}
        )

    # lookup the token
    try:
        token = NFCToken.objects.get(uid=uid)
    except NFCToken.DoesNotExist:
        token = NFCToken(uid=uid)
        token_sighting(token, location, False, type_="auth")
        return JsonResponse(
            {"found": False, "authorized": False, "reason": "Token not found"}
        )

    if not (token.enabled and token.user and token.user.is_active):
        token_sighting(token, location, False, type_="auth")
        return JsonResponse(
            {
                "found": False,
                "authorized": False,
                "reason": "Token not associated or enabled",
            }
        )

    if exclude_groups:
        for group in get_groups(token.user):
            if group in exclude_groups:
                token_sighting(token, location, False, type_="auth")
                return JsonResponse(
                    {
                        "found": True,
                        "authorized": False,
                        "reason": "In excluded group(s)",
                    }
                )

    user_groups = get_groups(token.user)
    matched_groups = []
    if required_groups:
        found = False
        for group in user_groups:
            if group in required_groups:
                matched_groups.append(group)
                found = True
        if not found:
            token_sighting(token, location, False, type_="auth")
            return JsonResponse(
                {
                    "found": True,
                    "authorized": False,
                    "reason": "Not in required group(s)",
                }
            )

    reply = {
        "found": True,
        "authorized": True,
        "username": token.user.username,
    }
    if request.user.has_perm("nfctokens.auth_token_name"):
        reply["name"] = token.user.get_full_name()
    if request.user.has_perm("nfctokens.auth_token_email"):
        reply["email"] = token.user.email
    if request.user.has_perm("nfctokens.auth_token_groups"):
        reply["groups"] = user_groups
    token_sighting(token, location, True, type_="auth")
    return JsonResponse(reply)
