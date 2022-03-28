# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import SSHKey


class SSHKeyAddForm(ModelForm):
    class Meta:
        model = SSHKey
        fields = ["key", "comment", "enabled"]


class SSHKeyEditForm(ModelForm):
    class Meta:
        model = SSHKey
        fields = ["key", "comment", "enabled"]


@login_required
def mysshkeys(request):
    context = {
        "sshkeys": request.user.sshkey_set.all(),
    }
    return render(request, "posixusers/mysshkeys.html", context)


@login_required
def mysshkeys_add(request, uid=None):
    if request.method == "POST":
        sshkey = SSHKey(user=request.user)
        sshkey.enabled = True
        form = SSHKeyAddForm(request.POST, instance=sshkey)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "SSH key added.")
            return HttpResponseRedirect(reverse("posixusers_sshkeys"))
    else:
        form = SSHKeyAddForm()
    context = {"form": form}
    return render(request, "posixusers/mysshkeys_add.html", context)


@login_required
def mysshkeys_edit(request, pk):
    sshkey = request.user.sshkey_set.get(pk=pk)
    if request.method == "POST":
        form = SSHKeyEditForm(request.POST, instance=sshkey)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "SSH key updated.")
            return HttpResponseRedirect(reverse("posixusers_sshkeys"))
    else:
        form = SSHKeyEditForm(instance=sshkey)
    context = {"form": form}
    return render(request, "posixusers/mysshkeys_edit.html", context)


@login_required
def mysshkeys_delete(request, pk):
    sshkey = request.user.sshkey_set.get(pk=pk)
    if request.method == "POST":
        sshkey.delete()
        messages.add_message(request, messages.SUCCESS, "SSH key deleted.")
        return HttpResponseRedirect(reverse("posixusers_sshkeys"))
    else:
        return render(request, "posixusers/mysshkeys_delete.html")


@login_required
@require_POST
def mysshkeys_enable(request, pk):
    sshkey = request.user.sshkey_set.get(pk=pk)
    sshkey.enabled = True
    sshkey.save()
    messages.add_message(request, messages.SUCCESS, "SSH key enabled.")
    return HttpResponseRedirect(reverse("posixusers_sshkeys"))


@login_required
@require_POST
def mysshkeys_disable(request, pk):
    sshkey = request.user.sshkey_set.get(pk=pk)
    sshkey.enabled = False
    sshkey.save()
    messages.add_message(request, messages.SUCCESS, "SSH key disabled.")
    return HttpResponseRedirect(reverse("posixusers_sshkeys"))
