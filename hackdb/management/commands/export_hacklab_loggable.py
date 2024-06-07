# SPDX-FileCopyrightText: 2022-2024 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import json
import sys
from types import NoneType

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db.models.fields import Field
from django.db.models.fields.related import RelatedField

from apikeys.models import APIKey


def obj_to_dict(obj, ignore=["id"], redact=["password"]):
    data = {}

    for field in obj._meta.get_fields():
        if field.name in ignore:
            pass
        elif field.name in redact:
            data[field.name] = "*redacted*"
        elif isinstance(field, RelatedField):
            pass
        elif isinstance(field, Field):
            if hasattr(obj, f"get_{field.name}_display"):
                data[field.name] = getattr(obj, f"get_{field.name}_display")()
            else:
                value = getattr(obj, field.name)
                if type(value) in [bool, float, int, NoneType]:
                    data[field.name] = value
                else:
                    data[field.name] = str(value)

    return data


def user_to_dict(user):
    data = {"user": obj_to_dict(user, ignore=["id", "last_login"], redact=[])}

    try:
        data["member"] = obj_to_dict(user.member)
    except ObjectDoesNotExist:
        data["member"] = None

    try:
        data["discorduser"] = obj_to_dict(user.discorduser)
    except ObjectDoesNotExist:
        data["discorduser"] = None

    try:
        data["posix"] = obj_to_dict(user.posix, redact=[])
    except ObjectDoesNotExist:
        data["posix"] = None

    data["groups"] = list(group.name for group in user.groups.order_by("name"))
    data["groupownerships"] = list(
        groupownership.group.name
        for groupownership in user.groupownerships.order_by("group__name")
    )

    data["permissions"] = list(
        str(permission) for permission in user.user_permissions.all()
    )
    data["emailaddresses"] = list(map(obj_to_dict, user.emailaddress_set.all()))
    data["membershipterms"] = list(map(obj_to_dict, user.membershipterm_set.all()))
    data["sshkeys"] = list(map(obj_to_dict, user.sshkey_set.all()))

    data["nfctokens"] = list(
        obj_to_dict(nfctoken, ignore=["id", "last_location", "last_seen"])
        for nfctoken in user.nfctokens.order_by("uid")
    )
    # data["nfctokenlogs"] = list(map(obj_to_dict, user.nfctokenlogs.all()))

    return data


def group_to_dict(group):
    data = {"group": obj_to_dict(group)}

    try:
        data["posix"] = obj_to_dict(group.posix)
    except ObjectDoesNotExist:
        data["posix"] = None

    try:
        data["properties"] = obj_to_dict(group.properties)
    except ObjectDoesNotExist:
        data["properties"] = None

    data["members"] = list(user.username for user in group.user_set.all())
    data["owners"] = list(ownership.user.username for ownership in group.owners.all())
    data["permissions"] = list(
        str(permission) for permission in group.permissions.all()
    )

    return data


def apikey_to_dict(apikey):
    data = {"apikey": obj_to_dict(apikey)}
    data["permissions"] = list(
        str(permission) for permission in apikey.permissions.all()
    )

    return data


class Command(BaseCommand):
    help = "Exports data to a format that will later be diffed and logged"

    def handle(self, *args, **options):
        output = {
            "users": [],
            "groups": [],
            "apikeys": [],
        }

        for user in get_user_model().objects.order_by("username"):
            output["users"].append(user_to_dict(user))

        for group in Group.objects.order_by("name"):
            output["groups"].append(group_to_dict(group))

        for apikey in APIKey.objects.order_by("uuid"):
            output["apikeys"].append(apikey_to_dict(apikey))

        json.dump(output, sys.stdout, indent=2, sort_keys=True)
