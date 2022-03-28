#!/bin/sh
#
# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: CC0-1.0

set -e

mkdir -p /data/config /data/generated /data/database
chown -R django:django /data

cd /data
runuser -u django python /usr/src/app/manage.py check
runuser -u django python /usr/src/app/manage.py makemigrations
runuser -u django python /usr/src/app/manage.py migrate
exec runuser -u django python /usr/src/app/manage.py runserver 0.0.0.0:8000
