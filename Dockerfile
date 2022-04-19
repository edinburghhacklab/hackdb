# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: CC0-1.0

FROM python:3.10

WORKDIR /usr/src/app

COPY Pipfile Pipfile.lock ./
RUN apt-get update \
    && apt-get install -y --no-install-recommends pipenv \
    && rm -r /var/lib/apt/lists/* \
    && pipenv install --deploy --system

COPY . ./

ENV DJANGO_SETTINGS_MODULE=hackdb.settings_docker

RUN rm -f db.sqlite3 local_settings.py settings_local.py \
    && useradd django \
    && python manage.py check \
    && python manage.py makemigrations

COPY docker-entrypoint.sh /docker-entrypoint.sh

EXPOSE 8000
VOLUME [ "/data/config", "/data/database", "/data/static" ]
ENTRYPOINT ["/docker-entrypoint.sh"]
