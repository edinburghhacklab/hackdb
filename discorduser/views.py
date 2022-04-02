# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import datetime
import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .models import DiscordUser, DiscordVerificationToken


@never_cache
@permission_required("discorduser.get_discord_users")
def api_get_users(request):
    data = {}
    for discord_user in DiscordUser.objects.all():
        data[discord_user.discord_id] = {
            "username": discord_user.user.username,
            "groups": discord_user.user.profile.get_groups(),
            "name": discord_user.user.profile.display_name,
        }
    return JsonResponse(data)


@never_cache
@permission_required("discorduser.get_discord_users")
def api_get_user(request, discord_id):
    discord_user = DiscordUser.objects.get(discord_id=discord_id)
    return JsonResponse(
        {
            "username": discord_user.user.username,
            "groups": discord_user.user.profile.get_groups(),
            "name": discord_user.user.profile.display_name,
        }
    )


@never_cache
@require_POST
@permission_required(
    "discorduser.generate_discord_confirmation_token", raise_exception=True
)
def api_generate_token(request):
    request_data = json.loads(request.body.decode())

    user = get_user_model().objects.filter(username=request_data["username"]).first()
    if not user:
        return JsonResponse({"error": "Invalid user"})

    token = DiscordVerificationToken(
        user=user,
        discord_id=request_data["discord_id"],
        discord_username=request_data["discord_username"],
    )
    token.save()

    return JsonResponse(
        {
            "url": request.build_absolute_uri(
                reverse("discorduser_verify_token", args=[token.token])
            )
        }
    )


@login_required
def verify_token(request, token):
    delete_before = timezone.make_aware(datetime.datetime.now()) - datetime.timedelta(
        hours=24
    )
    DiscordVerificationToken.objects.filter(created__lt=delete_before).delete()

    try:
        token_object = DiscordVerificationToken.objects.get(token=token)
    except DiscordVerificationToken.DoesNotExist:
        context = {
            "error": "Invalid verification token",
        }
        return render(request, "discorduser/verify_token_error.html", context)

    if token_object.user != request.user:
        context = {
            "error": f"Verification token is for a different user",
        }
        return render(request, "discorduser/verify_token_error.html", context)

    if request.method != "POST":
        context = {
            "discord_id": token_object.discord_id,
            "discord_username": token_object.discord_username,
        }
        return render(request, "discorduser/verify_token.html", context)

    try:
        discord_user = request.user.discorduser
    except DiscordUser.DoesNotExist:
        discord_user = DiscordUser(user=request.user)

    discord_user.discord_id = token_object.discord_id
    discord_user.discord_username = token_object.discord_username
    discord_user.save()

    token_object.delete()

    context = {
        "discord_id": token_object.discord_id,
        "discord_username": token_object.discord_username,
    }
    return render(request, "discorduser/verify_token_complete.html", context)
