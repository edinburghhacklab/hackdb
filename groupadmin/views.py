# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST


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

    context = {"groups": [groups[name] for name in sorted(groups.keys())]}
    return render(request, "groupadmin/groups.html", context)


@login_required
def groupadmin_view(request, group_name):
    group = request.user.groupownerships.get(group__name=group_name).group

    new_users = {}
    for user in get_user_model().objects.filter(is_active=True):
        new_users[user.username] = user.id

    users = {}
    for user in group.user_set.all():
        del new_users[user.username]
        users[user.username] = {
            "id": user.id,
            "username": user.username,
        }

    context = {
        "group": group,
        "users": [users[username] for username in sorted(users.keys())],
        "new_users": [
            (new_users[username], username) for username in sorted(new_users.keys())
        ],
    }

    return render(request, "groupadmin/group_view.html", context)


@login_required
@require_POST
def groupadmin_add_user(request, group_name):
    group = request.user.groupownerships.get(group__name=group_name).group
    user = get_user_model().objects.get(id=int(request.POST["user_id"]))
    group.user_set.add(user)
    messages.add_message(request, messages.SUCCESS, f"User {user.username} added.")
    return HttpResponseRedirect(reverse("groupadmin_view", args=[group_name]))


@login_required
@require_POST
def groupadmin_remove_user(request, group_name, user_id):
    group = request.user.groupownerships.get(group__name=group_name).group
    user = get_user_model().objects.get(id=user_id)
    group.user_set.remove(user)
    messages.add_message(request, messages.SUCCESS, f"User {user.username} removed.")
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
