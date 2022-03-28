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

In views, use the permission_required decorator. If you use @csrf_exempt
then also add @apikey_required.

```
@csrf_exempt
@require_POST
@apikey_required
@permission_required("app1.permission123", raise_exception=True)
def my_view(...):
   ...
```
