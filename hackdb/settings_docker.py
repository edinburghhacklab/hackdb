# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import os

from .settings_common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "")

# SECURITY WARNING: don't run with debug turned on in production!
if os.getenv("DEBUG", "False").strip().lower() in ["true", "t", "yes", "y", "1"]:
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").strip().split()

STATIC_ROOT = "/data/static/"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/data/database/db.sqlite3",
    }
}

TEMPLATES[0]["DIRS"].insert(0, "/data/config/templates")

try:
    exec(open("/data/config/settings.py").read())
except FileNotFoundError:
    pass
