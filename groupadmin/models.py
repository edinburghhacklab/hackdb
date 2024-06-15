# SPDX-FileCopyrightText: 2023 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models


class GroupOwnership(models.Model):
    group = models.ForeignKey(Group, related_name="owners", on_delete=models.CASCADE)
    user = models.ForeignKey(
        get_user_model(), related_name="groupownerships", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("user", "group")

    def __str__(self):
        return f"{self.group.name}:{self.user.username}"


class GroupProperties(models.Model):
    group = models.OneToOneField(
        Group, related_name="properties", on_delete=models.CASCADE
    )
    description = models.CharField(max_length=255, blank=True, null=True)
    self_service = models.BooleanField(default=False)
    advertise_owners = models.BooleanField(default=False)
    owners_manage_owners = models.BooleanField(default=False)

    def __str__(self):
        return self.group.name
