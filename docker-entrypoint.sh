#!/bin/sh
#
# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: CC0-1.0

set -e

chown -R django:django /data/database /data/static || true

runuser -u django -- python manage.py check
runuser -u django -- python manage.py collectstatic --clear --no-input
runuser -u django -- python manage.py makemigrations
runuser -u django -- python manage.py migrate
exec runuser -u django -- python manage.py runserver 0.0.0.0:8000
