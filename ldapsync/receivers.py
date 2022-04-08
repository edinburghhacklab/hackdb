# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from posixusers.models import PosixGroup, PosixUser

from .utils import sync_group, sync_user


@receiver(post_save, sender=get_user_model())
def sync_ldap_user(sender, instance, **kwargs):
    if list(kwargs.get("update_fields")) == ["last_login"]:
        # skip update if last_login was the only change
        return
    try:
        sync_user(instance)
    except Exception as e:
        print(f"exception in ldapsync of {instance}: {e}")


@receiver(post_save, sender=PosixUser)
def sync_ldap_posix_user(sender, instance, **kwargs):
    try:
        sync_user(instance.user)
    except:
        pass


@receiver(post_save, sender=Group)
def sync_ldap_group(sender, instance, **kwargs):
    try:
        sync_group(instance)
    except:
        pass


@receiver(post_save, sender=PosixGroup)
def sync_ldap_posix_group(sender, instance, **kwargs):
    try:
        sync_group(instance.group)
    except:
        pass
