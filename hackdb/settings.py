# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from .settings_common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ""

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

try:
    exec(open("settings_local.py").read())
except FileNotFoundError:
    pass

try:
    exec(open("local_settings.py").read())
except FileNotFoundError:
    pass
