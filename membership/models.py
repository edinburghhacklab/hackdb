# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import datetime
import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max, Min, Q
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


class Member(models.Model):
    NON_MEMBER = 0
    APPLICANT = 1
    APPROVED = 2
    MEMBER = 3
    SUSPENDED = 4
    LEAVING = 5
    ALUMNI = 6
    MEMBERSHIP_STATUS_CHOICES = [
        (NON_MEMBER, "Non-member"),
        (APPLICANT, "Applicant"),
        (APPROVED, "Approved"),
        (MEMBER, "Member"),
        (SUSPENDED, "Suspended"),
        (LEAVING, "Leaving"),
        (ALUMNI, "Alumni"),
    ]

    user = models.OneToOneField(get_user_model(), on_delete=models.PROTECT)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    real_name = models.CharField(max_length=255, verbose_name="Real name")

    # contact details
    address_street1 = models.CharField(
        max_length=255, blank=True, verbose_name="Street Address"
    )
    address_street2 = models.CharField(
        max_length=255, blank=True, verbose_name="Street Address 2"
    )
    address_street3 = models.CharField(
        max_length=255, blank=True, verbose_name="Street Address 3"
    )
    address_locality = models.CharField(max_length=255, blank=True, verbose_name="Town")
    address_state = models.CharField(max_length=255, blank=True, verbose_name="County")
    address_postalcode = models.CharField(
        max_length=255, blank=True, verbose_name="Postcode"
    )
    address_country = CountryField(blank=True, verbose_name="Country")
    phone = PhoneNumberField(blank=True)
    xero_uuid = models.UUIDField(null=True, blank=True, verbose_name="Xero UUID")

    # membership
    membership_number = models.PositiveIntegerField(unique=True, null=True, blank=True)
    membership_suspended = models.BooleanField(default=False)
    membership_status = models.SmallIntegerField(
        default=NON_MEMBER, choices=MEMBERSHIP_STATUS_CHOICES, editable=False
    )

    # admin
    notes = models.TextField(
        blank=True, help_text="These notes are visible to the user."
    )

    class Meta:
        permissions = [
            ("view_register", "Can view the register of members"),
            ("get_xero_contacts", "Can get contact data for Xero"),
            ("update_xero_contacts", "Can update member Xero UUIDs"),
        ]

    def __str__(self):
        return self.real_name or self.user.get_full_name()

    def clean(self):
        if self.membership_number is None:
            if self.is_member():
                highest_membership_number = Member.objects.aggregate(
                    n=Max("membership_number")
                )["n"]
                if highest_membership_number is None:
                    self.membership_number = 1
                else:
                    self.membership_number = highest_membership_number + 1
        self.fixup()

    # called automatically to make routine changes to the object
    def fixup(self):
        old_status = self.membership_status
        new_status = old_status

        active = False
        leaving = False
        alumni = False
        for term in self.user.membershipterm_set.all():
            if term.is_leaving():
                leaving = True
            elif term.is_active():
                active = True
            elif term.is_alumni():
                alumni = True

        if leaving:
            new_status = self.LEAVING
        elif active:
            new_status = self.MEMBER
        elif alumni:
            new_status = self.ALUMNI
        else:
            if old_status in [self.MEMBER, self.SUSPENDED, self.LEAVING, self.ALUMNI]:
                new_status = 0

        try:
            members_group = Group.objects.get(name="members")
            if new_status in [self.MEMBER, self.SUSPENDED, self.LEAVING]:
                # is member
                if not self.user.groups.contains(members_group):
                    self.user.groups.add(members_group)
            else:
                # not member
                if self.user.groups.contains(members_group):
                    self.user.groups.remove(members_group)
        except Group.DoesNotExist:
            print(f"members group does not exist, ignoring")

        if new_status != old_status:
            print(f"fix {self.user}: {old_status} -> {new_status}")
            self.membership_status = new_status
            return True
        else:
            return False

    def is_member(self):
        if self.membership_suspended is True:
            return False
        terms = self.user.membershipterm_set.filter(
            Q(start__lte=datetime.date.today()),
            Q(end__isnull=True) | Q(end__gte=datetime.date.today()),
        )
        if terms.count() > 0:
            return True
        return False

    is_member.boolean = True

    def first_joined(self):
        first_joined_date = self.user.membershipterm_set.aggregate(
            first_joined=Min("start")
        )["first_joined"]
        return first_joined_date


class MembershipTerm(models.Model):
    REGULAR = 0
    DISCOUNTED = 1
    FREE = 2
    REMOTE = 3
    MTYPE_CHOICES = [
        (REGULAR, "Regular"),
        (DISCOUNTED, "Discounted"),
        (FREE, "Free"),
        (REMOTE, "Remote"),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    start = models.DateField()
    end = models.DateField(null=True, blank=True)
    mtype = models.SmallIntegerField(default=0, choices=MTYPE_CHOICES)

    def __str__(self):
        if self.end:
            output = f"{self.user} {self.start}-{self.end}"
        else:
            output = f"{self.user} {self.start}-"
        if self.is_active():
            output = output + " [active]"
        if self.is_leaving():
            output = output + " [leaving]"
        if self.is_alumni():
            output = output + " [alumni]"
        return output

    def is_active(self):
        if self.start <= datetime.date.today():
            # starts today or in the past
            if self.end is None:
                # no end date
                return True
            elif self.end >= datetime.date.today():
                # ends today or in the future
                return True
            else:
                # end date is in the past
                return False
        else:
            # starts in the future
            return False

    is_active.boolean = True

    def is_leaving(self):
        if self.start <= datetime.date.today():
            # starts today or in the past
            if self.end is None:
                # no end date
                return False
            elif self.end >= datetime.date.today():
                # ends today or in the future
                return True
            else:
                # end date is in the past
                return False
        else:
            # starts in the future
            return False

    is_leaving.boolean = True

    def is_alumni(self):
        if self.start <= datetime.date.today():
            # starts today or in the past
            if self.end is None:
                # no end date
                return False
            elif self.end >= datetime.date.today():
                # ends today or in the future
                return False
            else:
                # end date is in the past
                return True
        else:
            # starts in the future
            return False

    is_alumni.boolean = True

    def clean(self):
        if self.user.member:
            self.user.member.fixup()


class MembershipSponsor(models.Model):
    sponsor = models.ForeignKey(
        get_user_model(), related_name="sponsees", on_delete=models.CASCADE
    )
    sponsee = models.ForeignKey(
        get_user_model(), related_name="sponsors", on_delete=models.CASCADE
    )
    date = models.DateField(null=False, blank=False, auto_now_add=True)

    class Meta:
        unique_together = ("sponsor", "sponsee")

    def clean(self):
        if self.sponsor == self.sponsee:
            raise ValidationError("Sponsor and sponsee cannot be the same user")
