# SPDX-FileCopyrightText: 2022-2024 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import random
import uuid

from django.contrib.auth.models import AnonymousUser, Permission
from django.db import models


def generate_key():
    return "".join(
        random.choices(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789", k=64
        )
    )


class APIKey(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    key = models.CharField(
        max_length=128,
        unique=True,
        default=generate_key,
    )
    description = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)
    expires = models.DateTimeField(null=True, blank=True)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
    )

    class Meta:
        verbose_name = "API key"

    def __str__(self):
        return str(self.uuid)


class APIUser(AnonymousUser):
    _apikey = None
    _permissions = set()

    def __str__(self):
        return f"APIUser #{self._apikey.uuid}"

    def __init__(self, apikey):
        self._apikey = apikey
        perms = apikey.permissions.values_list(
            "content_type__app_label", "codename"
        ).order_by()
        setattr(self, "_permissions", {f"{ct}.{name}" for ct, name in perms})
        print(self)

    def get_user_permissions(self):
        return self._permissions

    def has_perm(self, perm, obj=None):
        return perm in self._permissions

    def has_perms(self, perm_list, obj=None):
        return all(self.has_perm(perm, obj) for perm in perm_list)
