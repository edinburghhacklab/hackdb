# SPDX-FileCopyrightText: 2022-2024 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import datetime

from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class UnassignedTokenManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(user__isnull=True)


class RecentTokenManager(models.Manager):
    def get_queryset(self):
        t = timezone.now() - datetime.timedelta(minutes=5)
        return super().get_queryset().filter(user__isnull=True, last_seen__gte=t)


class NFCToken(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="nfctokens",
    )
    uid = models.CharField(
        max_length=32,
        unique=True,
        verbose_name="UID",
        validators=[
            RegexValidator(
                regex=r"^([0-9a-f]{8}|[0-9a-f]{14}|[0-9a-f]{20})$",
                message="Enter a valid UID of 8, 14 or 20 hexadecimal digits",
            ),
            RegexValidator(
                regex=r"^08[0-9a-f]{6}$",
                message="This is a randomly-generated UID which cannot be used for authentication",
                inverse_match=True,
            ),
            # Common fixed UIDs, not unique
            RegexValidator(
                regex=r"^(0{8}|0{14}|0{20}|f{8}|f{14}|f{20}|01020304|01020304050607|04ffffff|12345678)$",
                message="This is a common fixed/non-unique UID which cannot be used for authentication",
                inverse_match=True,
            ),
            # Invalid due to cascading rules (byte 0 of a 4-byte UID cannot be 0x88)
            RegexValidator(
                regex=r"^88[0-9a-f]{6}$",
                message="This is an invalid UID (contains a cascade tag)",
                inverse_match=True,
            ),
            # Invalid due to cascading rules (byte 3 of a 7-byte UID cannot be 0x88)
            RegexValidator(
                regex=r"^[0-9a-f]{6}88[0-9a-f]{6}$",
                message="This is an invalid UID (contains a cascade tag)",
                inverse_match=True,
            ),
            # Invalid due to cascading rules (byte 3 of a 10-byte UID cannot be 0x88)
            RegexValidator(
                regex=r"^[0-9a-f]{6}88[0-9a-f]{12}$",
                message="This is an invalid UID (contains a cascade tag)",
                inverse_match=True,
            ),
        ],
    )
    description = models.CharField(max_length=255, blank=True)
    enabled = models.BooleanField(default=True)
    last_edit = models.DateTimeField(editable=False, default=timezone.now)
    last_seen = models.DateTimeField(null=True, blank=True, editable=False)
    last_location = models.CharField(
        null=True, blank=True, max_length=255, editable=False
    )

    objects = models.Manager()
    unassigned_objects = UnassignedTokenManager()
    recent_objects = RecentTokenManager()

    class Meta:
        verbose_name = "NFC Token"
        permissions = [
            ("auth_token", "Can authenticate a token"),
            ("auth_token_name", "Can see name during authentication"),
            ("auth_token_email", "Can see email during authentication"),
            ("auth_token_groups", "Can see groups during authentication"),
            ("export_tokens", "Can export all tokens"),
            ("self_configure_token", "Can configure own NFC Token"),
        ]

    def __str__(self):
        return self.uid

    def clean(self):
        if self.uid is not None:
            self.uid = self.uid.strip().lower()


class NFCTokenLog(models.Model):
    timestamp = models.DateTimeField(null=False, blank=False, editable=False)
    user = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name="nfctokenlogs",
    )
    token = models.ForeignKey(
        NFCToken, null=True, blank=True, editable=False, on_delete=models.SET_NULL
    )
    location = models.CharField(max_length=255, editable=False)
    uid = models.CharField(max_length=32, editable=False)
    username = models.CharField(max_length=255, blank=True, editable=False)
    name = models.CharField(max_length=255, blank=True, editable=False)
    token_description = models.CharField(max_length=255, blank=True, editable=False)
    authorized = models.BooleanField(editable=False, null=True, blank=True)
    ltype = models.CharField(
        max_length=32, editable=False, default="unknown", verbose_name="Type"
    )

    class Meta:
        verbose_name = "NFC Token Log"
        permissions = [
            ("self_view_tokenlog", "Can view own NFC Token Log"),
        ]

    def save(self, *args, **kwargs):
        if self.id is None:
            super().save(*args, **kwargs)
        else:
            # we're only allowed to save new objects
            # don't allow changing of existing objects
            return
