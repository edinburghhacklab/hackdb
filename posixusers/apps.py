# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.apps import AppConfig


class PosixusersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "posixusers"

    def ready(self):
        from . import receivers
