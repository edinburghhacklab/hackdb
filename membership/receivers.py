# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.models import Group
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Member, MembershipTerm


@receiver(post_delete, sender=MembershipTerm)
def membership_term_post_delete(sender, instance, **kwargs):
    if instance.user.member.fixup():
        instance.user.member.save()


@receiver(post_save, sender=MembershipTerm)
def membership_term_post_save(sender, instance, **kwargs):
    if instance.user.member.fixup():
        instance.user.member.save()


@receiver(post_save, sender=Member)
def member_post_save(sender, instance, **kwargs):
    name = instance.display_name or instance.real_name
    update_fields = []
    if instance.user.first_name != name:
        instance.user.first_name = name
        update_fields.append("first_name")
    if instance.user.last_name != "":
        instance.user.last_name = ""
        update_fields.append("last_name")
    if update_fields:
        instance.user.save(update_fields=update_fields)

    try:
        datasharing_group = Group.objects.get(name="sharealike")
        if instance.privacy > 1:
            if instance.user.groups.contains(datasharing_group):
                instance.user.groups.remove(datasharing_group)
        else:
            if not instance.user.groups.contains(datasharing_group):
                instance.user.groups.add(datasharing_group)
    except Group.DoesNotExist:
        print(f"sharealike group does not exist, ignoring")
