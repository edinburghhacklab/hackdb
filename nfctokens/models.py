# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
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
                regex=r"^\s*([0-9a-fA-F]{8}|[0-9a-fA-F]{14}|[0-9a-fA-F]{20})\s*$",
                message="Enter a valid UID of 8, 14 or 20 hexadecimal digits",
            ),
            RegexValidator(
                regex=r"^\s*08[0-9a-fA-F]{6}\s*$",
                message="This is a randomly-generated UID which cannot be used for authentication",
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
