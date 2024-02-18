# SPDX-FileCopyrightText: 2024 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: CC0-1.0

FROM python:3.12

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --require-hashes -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=hackdb.settings_docker

RUN useradd django \
    && python manage.py check \
    && python manage.py makemigrations

COPY docker-entrypoint.sh /docker-entrypoint.sh

EXPOSE 8000
VOLUME [ "/data/config", "/data/database", "/data/static" ]
ENTRYPOINT ["/docker-entrypoint.sh"]
