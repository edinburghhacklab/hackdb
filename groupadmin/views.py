# SPDX-FileCopyrightText: 2023-2024 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import GroupOwnership


@login_required
def groupadmin_list(request):
    groups = {}

    # groups where the user is a member
    for group in request.user.groups.all():
        groups[group.name] = {"object": group, "member": True}

    # groups where the user is an owner
    for ownership in request.user.groupownerships.all():
        group = ownership.group
        if group.name not in groups:
            groups[group.name] = {"object": group}
        groups[group.name]["owner"] = True

    # groups that are configured for self-service
    for group in Group.objects.filter(properties__self_service=True):
        if group.name not in groups:
            groups[group.name] = {"object": group}

    # groups that are configured to advertise owners
    for group in Group.objects.filter(properties__advertise_owners=True):
        if group.name not in groups:
            groups[group.name] = {"object": group}
        if group.owners.count() > 0:
            groups[group.name]["owners_text"] = ", ".join(
                sorted(
                    owner.user.get_full_name() or owner.user.get_username()
                    for owner in group.owners.all()
                )
            )

    context = {"groups": [groups[name] for name in sorted(groups.keys())]}
    return render(request, "groupadmin/groups.html", context)


@login_required
def groupadmin_view(request, group_name):
    group = request.user.groupownerships.get(group__name=group_name).group

    new_members = {}
    for user in get_user_model().objects.filter(is_active=True):
        new_members[user.username] = {
            "id": user.id,
            "username": user.username,
            "full_name": user.get_full_name(),
        }
    new_owners = new_members.copy()

    members = {}
    for user in group.user_set.all():
        try:
            del new_members[user.username]
        except KeyError:
            pass
        members[user.username] = {
            "id": user.id,
            "username": user.username,
            "full_name": user.get_full_name(),
        }

    owners = {}
    for groupownership in group.owners.all():
        user = groupownership.user
        try:
            del new_owners[user.username]
        except KeyError:
            pass
        owners[user.username] = {
            "id": user.id,
            "username": user.username,
            "full_name": user.get_full_name(),
        }

    context = {
        "group": group,
        "members": [members[username] for username in sorted(members.keys())],
        "owners": [owners[username] for username in sorted(owners.keys())],
        "new_members": [
            (new_members[username]["id"], new_members[username])
            for username in sorted(new_members.keys())
        ],
        "new_owners": [
            (new_owners[username]["id"], new_owners[username])
            for username in sorted(new_owners.keys())
        ],
    }

    return render(request, "groupadmin/group_view.html", context)


@login_required
@require_POST
def groupadmin_add_member(request, group_name):
    group = request.user.groupownerships.get(group__name=group_name).group
    user = get_user_model().objects.get(id=int(request.POST["user_id"]))
    group.user_set.add(user)
    messages.add_message(request, messages.SUCCESS, f"Member {user.username} added.")
    return HttpResponseRedirect(reverse("groupadmin_view", args=[group_name]))


@login_required
@require_POST
def groupadmin_remove_member(request, group_name, user_id):
    group = request.user.groupownerships.get(group__name=group_name).group
    user = get_user_model().objects.get(id=user_id)
    group.user_set.remove(user)
    messages.add_message(request, messages.SUCCESS, f"Member {user.username} removed.")
    return HttpResponseRedirect(reverse("groupadmin_view", args=[group_name]))


@login_required
@require_POST
def groupadmin_add_owner(request, group_name):
    group = request.user.groupownerships.get(group__name=group_name).group
    user = get_user_model().objects.get(id=int(request.POST["user_id"]))
    if request.user == user:
        # this condition should never match, added just-in-case
        return HttpResponseForbidden("Cannot add self")
    if not group.properties.owners_manage_owners:
        return HttpResponseForbidden("Cannot manage owners")
    GroupOwnership.objects.create(group=group, user=user)
    messages.add_message(request, messages.SUCCESS, f"Owner {user.username} added.")
    return HttpResponseRedirect(reverse("groupadmin_view", args=[group_name]))


@login_required
@require_POST
def groupadmin_remove_owner(request, group_name, user_id):
    group = request.user.groupownerships.get(group__name=group_name).group
    user = get_user_model().objects.get(id=user_id)
    if request.user == user:
        return HttpResponseForbidden("Cannot remove self")
    if not group.properties.owners_manage_owners:
        return HttpResponseForbidden("Cannot manage owners")
    GroupOwnership.objects.get(group=group, user=user).delete()
    messages.add_message(request, messages.SUCCESS, f"Owner {user.username} removed.")
    return HttpResponseRedirect(reverse("groupadmin_view", args=[group_name]))


@login_required
@require_POST
def groupadmin_join(request, group_name):
    group = Group.objects.get(name=group_name, properties__self_service=True)
    group.user_set.add(request.user)
    messages.add_message(
        request, messages.SUCCESS, f"You have joined the {group.name} group."
    )
    return HttpResponseRedirect(reverse("groupadmin_list"))


@login_required
@require_POST
def groupadmin_leave(request, group_name):
    group = Group.objects.get(name=group_name, properties__self_service=True)
    group.user_set.remove(request.user)
    messages.add_message(
        request, messages.SUCCESS, f"You have left the {group.name} group."
    )
    return HttpResponseRedirect(reverse("groupadmin_list"))
