# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from posixusers.models import PosixGroup, PosixUser, SSHKey

from .utils import sync_group, sync_user


@receiver(post_save, sender=get_user_model())
def sync_ldap_user(sender, instance, update_fields=[], **kwargs):
    if update_fields and list(update_fields) == ["last_login"]:
        # skip update if last_login was the only change
        return
    try:
        print(f"ldapsync user {instance}")
        sync_user(instance)
    except Exception as e:
        print(f"Exception in ldapsync of {instance}: {e}")


@receiver(post_save, sender=PosixUser)
def sync_ldap_posix_user(sender, instance, **kwargs):
    try:
        print(f"ldapsync user {instance.user} (for PosixUser)")
        sync_user(instance.user)
    except Exception as e:
        print(f"Exception in ldapsync of {instance}: {e}")


@receiver(post_save, sender=SSHKey)
def sync_ldap_posix_sshkey(sender, instance, **kwargs):
    try:
        print(f"ldapsync user {instance.user} (for SSHKey)")
        sync_user(instance.user)
    except Exception as e:
        print(f"Exception in ldapsync of {instance}: {e}")


@receiver(post_save, sender=Group)
def sync_ldap_group(sender, instance, **kwargs):
    try:
        print(f"ldapsync group {instance}")
        sync_group(instance)
    except Exception as e:
        print(f"Exception in ldapsync of {instance}: {e}")


@receiver(post_save, sender=PosixGroup)
def sync_ldap_posix_group(sender, instance, **kwargs):
    try:
        print(f"ldapsync user {instance.group} (for PosixGroup)")
        sync_group(instance.group)
    except Exception as e:
        print(f"Exception in ldapsync of {instance}: {e}")


@receiver(m2m_changed, sender=Group.user_set.through)
def sync_ldap_group_m2m(sender, instance, *, action=None, **kwargs):
    if action in ["post_add", "post_remove"]:
        try:
            print(f"ldapsync group {instance} (for membership)")
            sync_group(instance)
        except Exception as e:
            print(f"Exception in ldapsync of {instance}: {e}")


# @receiver(post_save)
# def test_post_save(sender, instance, **kwargs):
#     print(f"POST_SAVE sender={sender} instance={instance} kwargs={kwargs}")


# @receiver(m2m_changed)
# def test_m2m_changed(sender, instance, **kwargs):
#     print(f"M2M_CHANGED sender={sender} instance={instance} kwargs={kwargs}")
