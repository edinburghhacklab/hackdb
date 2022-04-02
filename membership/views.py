# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import json

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import ModelForm
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from .models import Member


class UserSelfForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name"]


class MemberSelfForm(ModelForm):
    class Meta:
        model = Member
        fields = [
            "real_name",
            "address_street1",
            "address_street2",
            "address_street3",
            "address_locality",
            "address_state",
            "address_postalcode",
            "address_country",
            "phone",
        ]


@login_required
def profile(request):
    if request.method == "POST":
        user_form = UserSelfForm(request.POST, prefix="user", instance=request.user)
        try:
            member_form = MemberSelfForm(prefix="member", instance=request.user.member)
        except Member.DoesNotExist:
            member_form = MemberSelfForm(
                prefix="member", instance=Member(user=request.user)
            )
        member_form = MemberSelfForm(
            request.POST, prefix="member", instance=request.user.member
        )
        if user_form.is_valid() and member_form.is_valid():
            user_form.save()
            member_form.save()

            messages.add_message(request, messages.SUCCESS, "Member profile updated.")
            return HttpResponseRedirect(reverse("home"))
    else:
        user_form = UserSelfForm(prefix="user", instance=request.user)
        try:
            member_form = MemberSelfForm(prefix="member", instance=request.user.member)
        except Member.DoesNotExist:
            member_form = MemberSelfForm(prefix="member")
    context = {
        "user_form": user_form,
        "member_form": member_form,
    }
    return render(request, "membership/profile.html", context)


@login_required
@permission_required("membership.view_register")
def show_register(request):
    users = []
    for user in (
        get_user_model()
        .objects.filter(member__isnull=False)
        .order_by("member__real_name")
    ):
        users.append(user)
    context = {"users": users}
    return render(request, "membership/register.html", context)


@login_required
def overview(request):
    return render(request, "membership/overview.html")


def member_count(request):
    count = 0
    for user in get_user_model().objects.all():
        if user.member.is_member():
            count = count + 1
    return JsonResponse({"members": count})


@require_GET
@permission_required("membership.get_xero_contacts")
def xero_contacts_json(request):
    data = {}
    for member in Member.objects.all():
        if member.xero_uuid or member.membership_status in [1, 2, 3]:
            record = {
                "uuid": str(member.uuid),
                "xero_uuid": None,
                "name": member.real_name,
                "email": member.user.email,
                "phone": "",
                "address_street1": member.address_street1,
                "address_street2": member.address_street2,
                "address_street3": member.address_street3,
                "address_locality": member.address_locality,
                "address_state": member.address_state,
                "address_postalcode": member.address_postalcode,
                "address_country": "",
                "member": member.is_member(),
            }
            if member.xero_uuid:
                record["xero_uuid"] = str(member.xero_uuid)
            if member.phone:
                record["phone"] = str(member.phone)
            if member.address_country:
                record["address_country"] = member.address_country.name
            data[record["uuid"]] = record
    return JsonResponse(data)


@require_POST
@permission_required("membership.update_xero_contacts")
def xero_update_uuid(request):
    data = json.loads(request.body.decode())
    data["uuid"] = data["uuid"].strip().lower().replace("-", "")
    data["xero_uuid"] = data["xero_uuid"].strip().lower().replace("-", "")
    try:
        member = Member.objects.get(uuid=data["uuid"])
        if member.xero_uuid:
            if (
                str(member.xero_uuid).strip().lower().replace("-", "")
                == data["xero_uuid"]
            ):
                return JsonResponse({"status": "ok", "message": "No change required"})
            else:
                return JsonResponse(
                    {"status": "error", "message": "Conflicting UUID provided"}
                )
        else:
            member.xero_uuid = data["xero_uuid"]
            member.save()
            return JsonResponse({"status": "ok", "message": "Updated"})
    except Member.DoesNotExist:
        return JsonResponse({"status": "error", "message": "UUID not found"})
