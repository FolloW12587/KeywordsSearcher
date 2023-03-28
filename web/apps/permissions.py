from typing import Any, Callable
from django.db.models.query import QuerySet
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404

from web.kwfinder import models


def check_app_permissions(f: Callable[[Any, int], (HttpResponse)]):
    def wrapper(request, app_id: int, *args, **kwargs):
        if request.user.has_perm('kwfinder.can_see_all') or \
            (hasattr(request.user, 'profile') and
                request.user.profile.apps_allowed.contains(get_object_or_404(models.App, pk=app_id))):
            return f(request, app_id, *args, **kwargs)
        return HttpResponseForbidden("Forbidden")
    return wrapper


def get_allowed_apps(request) -> QuerySet[models.App]:
    if request.user.has_perm('kwfinder.can_see_all'):
        return models.App.objects.all()
    elif hasattr(request.user, 'profile'):
        return request.user.profile.apps_allowed.all()
    else:
        return models.App.objects.none()
