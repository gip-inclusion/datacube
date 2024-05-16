import os


SPOCK_ENVIRONMENT = "DEV"
os.environ["SPOCK_ENVIRONMENT"] = SPOCK_ENVIRONMENT

from .base import *  # noqa: E402,F403


SECRET_KEY = "foobar"
ALLOWED_HOSTS = []

# We *want* to do the same `collectstatic` on the CI than on PROD to catch errors early,
# but we don't want to do it when running the test suite locally for performance reasons.
if not os.getenv("CI", False):
    # `ManifestStaticFilesStorage` (used in base settings) requires `collectstatic` to be run.
    STORAGES["staticfiles"]["BACKEND"] = "django.contrib.staticfiles.storage.StaticFilesStorage"  # noqa: F405
