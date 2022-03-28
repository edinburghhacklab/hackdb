# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PosixGroup, PosixUser


@receiver(post_save, sender=get_user_model())
def create_posixuser(sender, instance, **kwargs):
    try:
        PosixUser.objects.get(user=instance)
    except:
        PosixUser.objects.create(user=instance)


@receiver(post_save, sender=Group)
def create_posixgroup(sender, instance, **kwargs):
    try:
        PosixGroup.objects.get(group=instance)
    except:
        PosixGroup.objects.create(group=instance)
