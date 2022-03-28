# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.apps import AppConfig


class MembersConfig(AppConfig):
    name = "membership"

    def ready(self):
        from . import receivers
