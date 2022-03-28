# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import random
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Max


def next_uid():
    highest_uid = PosixUser.objects.aggregate(n=Max("uid"))["n"]
    if highest_uid is None:
        return settings.POSIXUSER_UID_MIN
    else:
        return highest_uid + 1


def next_gid():
    highest_gid = PosixGroup.objects.aggregate(n=Max("gid"))["n"]
    if highest_gid is None:
        return settings.POSIXUSER_GID_MIN
    else:
        return highest_gid + 1


def random_uid():
    for i in range(0, 10):
        next_uid = random.randint(
            settings.POSIXUSER_UID_MIN, settings.POSIXUSER_UID_MAX
        )
        if not PosixUser.objects.filter(uid=next_uid).exists():
            return next_uid


def random_gid():
    for i in range(0, 10):
        next_gid = random.randint(
            settings.POSIXUSER_GID_MIN, settings.POSIXUSER_GID_MAX
        )
        if not PosixGroup.objects.filter(gid=next_gid).exists():
            return next_gid


def default_uid():
    if settings.POSIXUSER_ID_MODE == "next":
        return next_uid()
    elif settings.POSIXUSER_ID_MODE == "random":
        return random_uid()


def default_gid():
    if settings.POSIXUSER_ID_MODE == "next":
        return next_gid()
    elif settings.POSIXUSER_ID_MODE == "random":
        return random_gid()


class PosixUser(models.Model):
    user = models.OneToOneField(
        get_user_model(), related_name="posix", on_delete=models.CASCADE
    )
    uid = models.PositiveBigIntegerField(
        unique=True,
        default=default_uid,
        validators=[
            MinValueValidator(1000),
            MaxValueValidator(4294967295),
        ],
    )
    shell = models.CharField(max_length=255, blank=True, default="/bin/bash")
    password = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "POSIX user"

    def __str__(self):
        return self.user.username


class PosixGroup(models.Model):
    group = models.OneToOneField(Group, related_name="posix", on_delete=models.CASCADE)
    gid = models.PositiveIntegerField(
        unique=True,
        default=default_gid,
        validators=[
            MinValueValidator(1000),
            MaxValueValidator(4294967295),
        ],
    )

    class Meta:
        verbose_name = "POSIX group"

    def __str__(self):
        return self.group.name


def parse_ssh_key(text):
    re1 = re.compile(r"(.+)\s+([a-z0-9\-]+)\s+([a-zA-Z0-9\+\/\=]+)(.*)")
    re2 = re.compile(r"([a-z0-9\-]+)\s+([a-zA-Z0-9\+\/\=]+)(.*)")

    m = re1.match(text)
    if m:
        options = m.group(1).strip()
        keytype = m.group(2).strip()
        keydata = m.group(3).strip()
        comment = m.group(4).strip()
        return options, keytype, keydata, comment

    m = re2.match(text)
    if m:
        options = ""
        keytype = m.group(1).strip()
        keydata = m.group(2).strip()
        comment = m.group(3).strip()
        return options, keytype, keydata, comment


class SSHKey(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    key = models.TextField()
    comment = models.CharField(max_length=255, blank=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = "SSH key"

    def __str__(self):
        if len(self.comment) > 0:
            return self.comment
        else:
            return self.key[0:20] + "..."

    def clean(self):
        if len(self.comment) == 0:
            parsed = parse_ssh_key(self.key)
            if parsed:
                self.comment = parsed[3]
