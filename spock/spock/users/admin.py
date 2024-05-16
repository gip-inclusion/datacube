from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from spock.users import models


@admin.register(models.User)
class UserAdmin(UserAdmin):
    pass
