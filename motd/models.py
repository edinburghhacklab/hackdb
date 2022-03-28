# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.db import models
from django.db.models import Q
from django.utils import timezone


class CurrentMessagesManager(models.Manager):
    def get_queryset(self):
        now = timezone.now()
        return (
            super()
            .get_queryset()
            .filter(
                Q(end__gte=now) | Q(end__isnull=True), start__lte=now, is_active=True
            )
        )


class MOTD(models.Model):
    start = models.DateTimeField(null=False, blank=False)
    end = models.DateTimeField(null=True, blank=True)
    message = models.TextField()
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = CurrentMessagesManager()

    class Meta:
        verbose_name = "Message of the day"
        verbose_name_plural = "Messages of the day"
