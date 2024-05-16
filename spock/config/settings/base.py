"""
Base settings to build other settings files upon.
https://docs.djangoproject.com/en/dev/ref/settings
"""

import os
import warnings

from dotenv import load_dotenv


load_dotenv()

# Django settings
# ---------------

_current_dir = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(_current_dir, "../.."))

APPS_DIR = os.path.abspath(os.path.join(ROOT_DIR, "spock"))

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "admin.datacube.gip-inclusion.org").split(",")

SITE_ID = 1


if "GDAL_LIBRARY_PATH" in os.environ:
    GDAL_LIBRARY_PATH = os.environ["GDAL_LIBRARY_PATH"]
if "GEOS_LIBRARY_PATH" in os.environ:
    GEOS_LIBRARY_PATH = os.environ["GEOS_LIBRARY_PATH"]

INSTALLED_APPS = [
    # Django apps.
    "django.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.gis",
    "django.contrib.postgres",
    "spock.users",
]

# TODO: Remove with Django 6.0
warnings.filterwarnings("ignore", "The FORMS_URLFIELD_ASSUME_HTTPS transitional setting is deprecated.")
FORMS_URLFIELD_ASSUME_HTTPS = True

MIDDLEWARE = [
    # Django stack
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(APPS_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

# Override default Django forms widgets templates.
# Requires django.forms in INSTALLED_APPS
# https://timonweb.com/django/overriding-field-widgets-in-django-doesnt-work-template-not-found-the-solution/
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

DATABASES = {
    "default": {
        "ATOMIC_REQUESTS": True,
        # Since we have the health checks enabled, no need to define a max age:
        # if the connection was closed on the database side, the check will detect it
        "CONN_MAX_AGE": None,
        "CONN_HEALTH_CHECKS": True,
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.getenv("PGDATABASE"),
        # The custom iptables rules forces us to use the direct host and port in production, the
        # usual one is unreachable.
        "HOST": os.getenv("PGHOST"),
        "PORT": os.getenv("PGPORT"),
        "USER": os.getenv("PGUSER"),
        "PASSWORD": os.getenv("PGPASSWORD"),
        "OPTIONS": {
            "connect_timeout": 5,
        },
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fr-FR"

TIME_ZONE = "Europe/Paris"

USE_TZ = True

DATE_INPUT_FORMATS = ["%d/%m/%Y", "%d-%m-%Y", "%d %m %Y"]


STATIC_ROOT = "staticfiles"
STATIC_URL = "/static/"

STATICFILES_DIRS = (os.path.join(ROOT_DIR, "static"),)

APPEND_SLASH = True

STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


CSRF_USE_SESSIONS = True

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_SECURE = True

# Force browser to end session when closing.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Since some browser restore session when restarting, the previous setting may not
# work as we want. This is why we ask Django to expire sessions in DB after 1 week
# of inactivity.
# -> https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies#define_the_lifetime_of_a_cookie
# In addition, the command shorten_active_sessions is run every week to force user to connect at least once per week
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7

X_FRAME_OPTIONS = "DENY"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
        "null": {"class": "logging.NullHandler"},
    },
    "loggers": {
        "": {"handlers": ["console"], "level": "INFO"},
        "django": {
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        },
        # Silence `Invalid HTTP_HOST header` errors.
        # This should be done at the HTTP server level when possible.
        # https://docs.djangoproject.com/en/3.0/topics/logging/#django-security
        "django.security.DisallowedHost": {
            "handlers": ["null"],
            "propagate": False,
        },
        "spock": {
            "level": os.getenv("SPOCK_LOG_LEVEL", "INFO"),
        },
    },
}

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)
