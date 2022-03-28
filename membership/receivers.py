# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import MembershipTerm


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
