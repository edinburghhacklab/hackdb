# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

from .models import APIUser


def apikey_test(user):
    if type(user) is APIUser:
        return True
    raise PermissionDenied


def apikey_required(function=None):
    actual_decorator = user_passes_test(apikey_test)
    if function:
        return actual_decorator(function)
    return actual_decorator
