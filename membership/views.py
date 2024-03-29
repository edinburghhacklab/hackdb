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

from .models import Member, MembershipTerm


class MemberSelfForm(ModelForm):
    class Meta:
        model = Member
        fields = [
            "real_name",
            "display_name",
            "address_street1",
            "address_street2",
            "address_street3",
            "address_locality",
            "address_state",
            "address_postalcode",
            "address_country",
            "phone",
            "privacy",
        ]
        help_texts = {
            "privacy": "This preference will apply to your access token logs.",
        }


@login_required
def profile(request):
    if request.method == "POST":
        try:
            member_form = MemberSelfForm(prefix="member", instance=request.user.member)
        except Member.DoesNotExist:
            member_form = MemberSelfForm(
                prefix="member", instance=Member(user=request.user)
            )
        member_form = MemberSelfForm(
            request.POST, prefix="member", instance=request.user.member
        )
        if member_form.is_valid():
            member_form.save()

            messages.add_message(request, messages.SUCCESS, "Member profile updated.")
            return HttpResponseRedirect(reverse("home"))
    else:
        try:
            member_form = MemberSelfForm(prefix="member", instance=request.user.member)
        except Member.DoesNotExist:
            member_form = MemberSelfForm(prefix="member")
    context = {
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
    terms = MembershipTerm.objects.order_by("user__member__real_name", "start")
    context = {"users": users, "terms": terms}
    return render(request, "membership/register.html", context)


@login_required
@permission_required("membership.view_register")
def show_register_with_display_names(request):
    users = []
    for user in (
        get_user_model()
        .objects.filter(member__isnull=False)
        .order_by("member__real_name")
    ):
        users.append(user)
    terms = MembershipTerm.objects.order_by("user__member__real_name", "start")
    context = {"users": users, "terms": terms}
    return render(request, "membership/register_with_display_names.html", context)


@login_required
@permission_required("membership.view_register")
def show_register_with_address(request):
    users = []
    for user in (
        get_user_model()
        .objects.filter(member__isnull=False)
        .order_by("member__real_name")
    ):
        users.append(user)
    terms = MembershipTerm.objects.order_by("user__member__real_name", "start")
    context = {"users": users, "terms": terms}
    return render(request, "membership/register_with_address.html", context)


@login_required
def overview(request):
    return render(request, "membership/overview.html")


def member_count(request):
    data = {
        "members": 0,
        "type": {
            x[1].lower(): 0 for x in MembershipTerm._meta.get_field("mtype").choices
        },
    }

    for member in Member.objects.all():
        if member.is_member():
            data["members"] += 1
            for term in member.user.membershipterm_set.all():
                if term.is_active:
                    mtype_text = term.get_mtype_display().lower()
                    data["type"][mtype_text] = data["type"].get(mtype_text, 0) + 1
                    break

    return JsonResponse(data)


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
