# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import base64

from .models import APIKey, APIUser


class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "HTTP_AUTHORIZATION" in request.META:
            auth_type, credentials = request.META["HTTP_AUTHORIZATION"].split(" ", 1)
            if auth_type.lower() == "bearer":
                try:
                    apikey = APIKey.objects.get(key=credentials)
                    request.user = APIUser(apikey)
                    return self.get_response(request)
                except APIKey.DoesNotExist:
                    pass
            elif auth_type.lower() == "basic":
                username, password = (
                    base64.b64decode(credentials).decode().split(":", 1)
                )
                try:
                    apikey = APIKey.objects.get(key=password)
                    request.user = APIUser(apikey)
                    return self.get_response(request)
                except APIKey.DoesNotExist:
                    pass

        if "X-API-Token" in request.headers:
            try:
                apikey = APIKey.objects.get(key=request.headers["X-API-Token"])
                request.user = APIUser(apikey)
                return self.get_response(request)
            except APIKey.DoesNotExist:
                pass

        if "X-API-Key" in request.META:
            try:
                apikey = APIKey.objects.get(request.headers["X-API-Key"])
                request.user = APIUser(apikey)
                return self.get_response(request)
            except APIKey.DoesNotExist:
                pass

        return self.get_response(request)
