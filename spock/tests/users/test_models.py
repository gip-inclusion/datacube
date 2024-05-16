from spock.users.models import User

from .factories import UserFactory


def test_user_factory():
    user = UserFactory()
    assert User.objects.get() == user
