# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Member, MembershipTerm


@receiver(post_delete, sender=MembershipTerm)
def membership_term_post_delete(sender, instance, **kwargs):
    print(f"{instance} deleted")
    if instance.user.member.fixup():
        instance.user.member.save()


@receiver(post_save, sender=MembershipTerm)
def membership_term_post_save(sender, instance, **kwargs):
    print(f"{instance} saved")
    if instance.user.member.fixup():
        instance.user.member.save()


@receiver(post_save, sender=Member)
def member_post_save(sender, instance, **kwargs):
    print(f"{instance} saved")
    name = instance.display_name or instance.real_name
    update_fields = []
    if instance.user.first_name != name:
        instance.user.first_name = name
        update_fields.append("first_name")
    if instance.user.last_name != "":
        instance.user.last_name = ""
        update_fields.append("last_name")
    if update_fields:
        print(f"saving user fields: {update_fields}")
        instance.user.save(update_fields=update_fields)
