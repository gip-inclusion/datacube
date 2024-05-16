# ruff: noqa: F405
import os


SPOCK_ENVIRONMENT = "DEV"
os.environ["SPOCK_ENVIRONMENT"] = SPOCK_ENVIRONMENT

from .test import *  # noqa: E402,F403


# Django settings
# ---------------
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "192.168.0.1", "0.0.0.0"]

SESSION_COOKIE_SECURE = False

AUTH_PASSWORD_VALIDATORS = []

INSTALLED_APPS.extend(
    [
        "django_extensions",
        "debug_toolbar",
    ]
)

INTERNAL_IPS = ["127.0.0.1"]

MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa F405
DEBUG_TOOLBAR_CONFIG = {
    # https://django-debug-toolbar.readthedocs.io/en/latest/panels.html#panels
    "DISABLE_PANELS": [
        "debug_toolbar.panels.redirects.RedirectsPanel",
        # ProfilingPanel makes the django admin extremely slow...
        "debug_toolbar.panels.profiling.ProfilingPanel",
    ],
    "SHOW_TEMPLATE_CONTEXT": True,
}

DATABASES["default"]["NAME"] = os.getenv("PGDATABASE", "spock")
DATABASES["default"]["HOST"] = os.getenv("PGHOST", "localhost")
DATABASES["default"]["PORT"] = os.getenv("PGPORT", "5432")
DATABASES["default"]["USER"] = os.getenv("PGUSER", "postgres")
DATABASES["default"]["PASSWORD"] = os.getenv("PGPASSWORD", "password")
