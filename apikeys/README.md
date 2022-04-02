This is a simple system for managing API keys and using them as an
alternative authorization method.

Add to INSTALLED_APPS and MIDDLEWARE.

```
INSTALLED_APPS = [
    ...
    "apikeys",
    ...
]

MIDDLEWARE = [
    ...
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # must appear at some point after AuthenticationMiddleware
    "apikeys.middleware.APIKeyMiddleware",
    ...
]
```

In views, use the @permission_required decorator. @csrf_exempt shouldn't
be required as the middleware will disable CSRF on a request with a
successful API authentication.

```
@require_POST
@permission_required("app1.permission123", raise_exception=True)
def my_view(...):
   ...
```
