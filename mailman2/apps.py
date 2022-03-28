# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.apps import AppConfig


class Mailman2Config(AppConfig):
    name = "mailman2"

    def ready(self):
        from . import receivers
