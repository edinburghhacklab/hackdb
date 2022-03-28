# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.crypto import get_random_string


def random_token():
    return get_random_string(16)


class DiscordUser(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    discord_id = models.BigIntegerField(unique=True)
    discord_username = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"id={self.discord_id} name={self.discord_username}"

    class Meta:
        permissions = [
            ("get_discord_users", "Can retrieve Discord user data"),
            (
                "generate_discord_confirmation_token",
                "Can generate Discord confirmation token",
            ),
        ]


class DiscordVerificationToken(models.Model):
    token = models.CharField(max_length=255, unique=True, default=random_token)
    created = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    discord_id = models.BigIntegerField()
    discord_username = models.CharField(max_length=255)

    def __str__(self):
        return f"id={self.discord_id} name={self.discord_username}"
