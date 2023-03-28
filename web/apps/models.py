from __future__ import annotations
from django.db import models
from django.contrib.auth.models import User

from web.kwfinder.models import App


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    apps_allowed = models.ManyToManyField(
        App, verbose_name="Разрешенные приложения")

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    @staticmethod
    def create_profile(user: User) -> Profile:
        profile = Profile(user=user)
        profile.save()
        return profile
