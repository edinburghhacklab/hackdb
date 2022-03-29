# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ""

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.humanize",
    "django_countries",
    "phonenumber_field",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.oauth2",
    "django_bootstrap5",
    "django_extensions",
    "hackdb",
    "apikeys",
    "datarequest",
    "discorduser",
    "groupadmin",
    "ldapsync",
    "mailman2",
    "membership",
    "motd",
    "nfctokens",
    "posixusers",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apikeys.middleware.APIKeyMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "hackdb.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["hackdb/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # `allauth` needs this from django
                "django.template.context_processors.request",
                "motd.context_processors.motd_messages",
                "mailman2.context_processors.mailman2_prompts",
            ],
        },
    },
]

WSGI_APPLICATION = "hackdb.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    # This isn't a validator. It captures the changed password to store an alternative hash.
    {
        "NAME": "posixusers.password_validation.UpdatePosixPassword",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-gb"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SITE_ID = 1

LOGIN_REDIRECT_URL = "home"

SOCIALACCOUNT_PROVIDERS = {}

COUNTRIES_FIRST = ["GB"]
PHONENUMBER_DEFAULT_REGION = "GB"

POSIXUSER_UID_MIN = 2000000000
POSIXUSER_UID_MAX = 2999999999
POSIXUSER_GID_MIN = 3000000000
POSIXUSER_GID_MAX = 3999999999
POSIXUSER_ID_MODE = "random"  # next, random

MAILMAN_URL = ""
MAILMAN_API_URL = ""
MAILMAN_API_USERNAME = ""
MAILMAN_API_PASSWORD = ""
MAILMAN_ENABLE_INTERACTIVE_CHANGES = False
MAILMAN_ENABLE_ADDRESS_CHANGES = False
MAILMAN_ENABLE_AUTO_SUBSCRIBE = False
MAILMAN_ENABLE_AUTO_UNSUBSCRIBE = False

try:
    exec(open("settings_local.py").read())
except FileNotFoundError:
    pass

try:
    exec(open("local_settings.py").read())
except FileNotFoundError:
    pass
