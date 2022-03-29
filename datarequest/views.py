# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from types import NoneType

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields import Field
from django.db.models.fields.related import RelatedField
from django.http import JsonResponse
from django.shortcuts import render

from mailman2 import mailmanapi


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
            value = getattr(obj, field.name)
            if type(value) in [bool, float, int, NoneType]:
                data[field.name] = value
            else:
                data[field.name] = str(value)

    return data


@login_required
def datarequest(request):
    return render(request, "datarequest/datarequest.html")


@login_required
def datarequest_download(request):

    data = {"user": obj_to_dict(request.user)}

    try:
        data["member"] = obj_to_dict(request.user.member)
    except ObjectDoesNotExist:
        data["member"] = None

    try:
        data["discorduser"] = obj_to_dict(request.user.discorduser)
    except ObjectDoesNotExist:
        data["discorduser"] = None

    data["groups"] = list(group.name for group in request.user.groups.order_by("name"))
    data["groupownerships"] = list(
        groupownership.group.name
        for groupownership in request.user.groupownerships.order_by("group__name")
    )

    data["emailaddresses"] = list(map(obj_to_dict, request.user.emailaddress_set.all()))
    data["membershipterms"] = list(
        map(obj_to_dict, request.user.membershipterm_set.all())
    )
    data["nfctokens"] = list(map(obj_to_dict, request.user.nfctokens.all()))
    data["nfctokenlogs"] = list(map(obj_to_dict, request.user.nfctokenlogs.all()))
    data["posix"] = obj_to_dict(request.user.posix)
    data["sshkeys"] = list(map(obj_to_dict, request.user.sshkey_set.all()))

    try:
        mailinglists_data = {}
        for address in request.user.emailaddress_set.filter(verified=True):
            mailinglists_data[address.email] = mailmanapi.get_member(address.email)
        data["mailinglists"] = mailinglists_data
    except:
        data["mailinglists"] = "*error-not-available*"

    return JsonResponse(data, json_dumps_params={"sort_keys": True, "indent": 2})
