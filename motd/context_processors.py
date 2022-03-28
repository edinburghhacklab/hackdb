# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from .models import MOTD


def motd_messages(request):
    return {
        "motd_messages": MOTD.active_objects,
    }
