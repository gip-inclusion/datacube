import functools

import factory.fuzzy
from django.contrib.auth.hashers import make_password

from spock.users import models


DEFAULT_PASSWORD = "P4ssw0rd!***"


@functools.cache
def default_password():
    return make_password(DEFAULT_PASSWORD)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User
        skip_postgeneration_save = True

    username = factory.Sequence("user_name{}".format)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.LazyFunction(default_password)
