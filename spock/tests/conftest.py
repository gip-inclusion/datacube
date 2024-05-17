import freezegun
import pytest
from django.contrib.gis.db.models.fields import get_srid_info
from django.db import connection
from django.test import Client

from tests.users.factories import UserFactory


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    """Automatically add pytest db marker if needed."""
    for item in items:
        markers = {marker.name for marker in item.iter_markers()}
        if "no_django_db" not in markers and "django_db" not in markers:
            item.add_marker(pytest.mark.django_db)


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def admin_client(client):
    user = UserFactory(is_superuser=True)
    client.force_login(user)
    return client


@pytest.fixture(autouse=True, scope="session")
def preload_spatial_reference(django_db_setup, django_db_blocker):
    """
    Any first acces to a PostGIS field with geodjango loads the associated spatial
    reference information in an memory cache within Django.
    This fixture ensures this cache has been filled so that we have a consistent amount
    of database requests between tests to avoid a potential source of flakiness.

    Make a request for every spatial reference in use in the project.
    """
    with django_db_blocker.unblock():
        get_srid_info(4326, connection)


@pytest.fixture()
def frozen_time():
    with freezegun.freeze_time("2024-05-20 16:11:34") as ft:
        yield ft
