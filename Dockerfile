# SPDX-FileCopyrightText: 2024-2025 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: CC0-1.0

FROM python:3.14
COPY --from=ghcr.io/astral-sh/uv:0.9.10 /uv /uvx /bin/

COPY . /app
WORKDIR /app
RUN uv sync --locked
ENV PATH="/app/.venv/bin:$PATH"

ENV DJANGO_SETTINGS_MODULE=hackdb.settings_docker

RUN useradd django \
    && python manage.py check \
    && python manage.py makemigrations

COPY docker-entrypoint.sh /docker-entrypoint.sh

EXPOSE 8000
VOLUME [ "/data/config", "/data/database", "/data/static" ]
ENTRYPOINT ["/docker-entrypoint.sh"]
