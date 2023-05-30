import json
import logging

from django.contrib.auth.decorators import login_required
from django.forms import modelform_factory
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.datastructures import MultiValueDictKeyError

from src.apps_state import check_app
from src.asoworld import add_app_to_asoworld, add_keyword_to_app_in_asoworld
from web.kwfinder import models, serializers
from web.kwfinder.services.proxy.mobile_proxy import MobileProxy
from web.kwfinder.services.proxy.simple_proxy import (
    create_proxy_requests_session, get_proxy, safe_proxy_repr)

from .models import Profile
from .permissions import check_app_permissions, get_allowed_apps

logger = logging.getLogger(__name__)


@login_required
def appsAnalytics(request):
    """View for showing apps analytics page"""
    apps = get_allowed_apps(request)

    apps = apps.order_by("-is_active", "num")
    return render(request, "apps/apps_info.html", {"apps": apps})


@check_app_permissions
@login_required
def appAnalytics(request, app_id: int):
    app = get_object_or_404(models.App, pk=app_id)
    keywords = app.keywords.all().order_by("name")
    return render(request, "apps/app_stats.html", {"app": app, "keywords": keywords})


@check_app_permissions
@login_required
def consoleDataAdd(request, app_id: int):
    app = get_object_or_404(models.App, pk=app_id)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Data is not a valid json"}, status=400)

        try:
            data = data["data"]

            for d in data:
                try:
                    keyword = models.Keyword.objects.get(id=d["keyword__id"])
                except models.Keyword.DoesNotExist:
                    continue

                console_data = models.ConsoleDailyData.objects.filter(
                    app=app, keyword=keyword, date=d["date"]).first()

                if not console_data:
                    console_data = models.ConsoleDailyData(
                        app=app, keyword=keyword, date=d["date"])

                console_data.views = d["views"]
                console_data.installs = d["installs"]
                console_data.save()

        except (ValueError, KeyError):
            return JsonResponse({"error": "Data is not valid"}, status=400)

        return JsonResponse({"success": True})

    keywords = app.keywords.all()
    message = None
    if "message" in request.session:
        message = request.session["message"]
        del request.session["message"]
    return render(request, "apps/console_data_add.html", {"app": app, "keywords": keywords, "message": message})


@check_app_permissions
@login_required
def consoleDataAddByFile(request, app_id: int):
    def __responseWithError(text: str) -> HttpResponse:
        message = {"text": text, "success": False}
        request.session["message"] = message
        return HttpResponseRedirect(f"/apps_info/{app.id}/console_data/")

    app = get_object_or_404(models.App, pk=app_id)

    if request.method == "POST":
        try:
            data = json.loads(request.FILES["file"].read())
        except json.JSONDecodeError:
            return __responseWithError("Ошибка при декодировании файла! Убедитесь в его целостности.")
        except MultiValueDictKeyError:
            return __responseWithError("Не удалось найти файл. Убедитесь, что вы его отправили!")

        serializer = serializers.ConsoleDailyAPIDataSerializer(
            data=data, many=True)

        if not serializer.is_valid():
            return __responseWithError("Данные в загруженном файле невалидны!")

        response_data = {
            "skipped": 0,
            "updated": 0,
            "created": 0,
            "keywords_created": 0,
            "keywords_failed_to_create": 0,
        }

        for data in serializer.data:
            if data["keyword"] == "Другое" or app.num != data["app_num"]:
                response_data["skipped"] += 1
                continue

            keyword = app.keywords.filter(
                name=data["keyword"], region=data["region"]).first()
            if not keyword:
                logger.debug(
                    f"Not found keyword {data['keyword']} in region {data['region']}")
                keyword = models.Keyword.objects.filter(
                    name=data["keyword"], region=data["region"]).first()
                if not keyword:
                    region = models.ASOWorldRegion.objects.filter(
                        code=data["region"]).first()

                    if not region:
                        continue

                    keyword = models.Keyword.objects.create(
                        name=data["keyword"], region=region)

                    if not add_keyword_to_app_in_asoworld(app, keyword):
                        app.keywords.remove(keyword)
                        if keyword.app_set.count() == 0:  # type: ignore
                            keyword.delete()

                        response_data["keywords_failed_to_create"] += 1
                        continue

                    response_data["keywords_created"] += 1

                app.keywords.add(keyword)

            consoleData = models.ConsoleDailyData.objects.filter(
                app=app, keyword=keyword, date=data["date"]).first()

            if not consoleData:
                models.ConsoleDailyData.objects.create(
                    app=app, keyword=keyword, date=data["date"], views=data["views"], installs=data["installs"]
                )
                response_data["created"] += 1
                continue

            consoleData.views = data["views"]
            consoleData.installs = data["installs"]
            consoleData.save()
            response_data["updated"] += 1

        message = {
            "text": f"Данных о ключах: пропущено - {response_data['skipped']}, обновлено - {response_data['updated']}, \
                создано - {response_data['created']}. Ключей: создано - {response_data['keywords_created']}, \
                ошибок при создании - {response_data['keywords_failed_to_create']}",
            "success": True,
        }
        request.session["message"] = message
        return HttpResponseRedirect(f"/apps_info/{app.id}/console_data/")

    return HttpResponseRedirect(f"/apps_info/{app.id}/console_data/")


@login_required
def add_app(request):
    Form = modelform_factory(models.App, exclude=[
                             "keywords", "is_active", "icon"])
    if request.method == "POST":
        form = Form(request.POST, request.FILES)

        if form.is_valid():
            app = form.save()
            app: models.App
            if not add_app_to_asoworld(app):
                app.delete()
                return render(
                    request,
                    "apps/app_add.html",
                    {
                        "form": form,
                        "error": "Ошибка при добавлении приложения в ASO World. \
                                Пожалуйста, обратитесь к администратору!",
                    },
                )

            if not request.user.has_perm("kwfinder.can_see_all"):
                if not hasattr(request.user, "profile"):
                    Profile.create_profile(user=request.user)

                profile = request.user.profile
                profile.apps_allowed.add(app)

            proxies = get_proxy()
            if not proxies:
                logger.error("Can't find proxy. Aborting!")
                return HttpResponseRedirect(f"/apps_info/{app.id}/")

            session = create_proxy_requests_session(proxy=proxies)
            if not session:
                logger.error(
                    f"Can't create session for proxy {safe_proxy_repr(proxies)}. Aborting!")
                return HttpResponseRedirect(f"/apps_info/{app.id}/")

            check_app(app, session)
            return HttpResponseRedirect(f"/apps_info/{app.id}/")
    else:
        form = Form()

    return render(request, "apps/app_add.html", {"form": form})


@check_app_permissions
@login_required
def app_keywords(request, app_id: int):
    app = get_object_or_404(models.App, pk=app_id)

    keywords = app.keywords.all().order_by("region", "name")
    positions = {
        keyword: keyword.apppositionscriptrundata_set.filter(
            app=app).order_by("-run__started_at").first()
        for keyword in keywords
    }
    return render(request, "apps/keywords/keywords.html", {"app": app, "positions": positions})


@check_app_permissions
@login_required
def app_keywords_analytics(request, app_id: int):
    app = get_object_or_404(models.App, pk=app_id)

    keywords = app.keywords.all().order_by("region", "name")
    return render(request, "apps/keywords/keywords_analytics.html", {"app": app, "keywords": keywords})


@check_app_permissions
@login_required
def add_keyword_to_app(request, app_id: int):
    app = get_object_or_404(models.App, pk=app_id)

    Form = modelform_factory(models.Keyword, fields="__all__")
    message = None
    if request.method == "POST":
        form = Form(request.POST)

        if form.is_valid():
            keyword = models.Keyword.objects.filter(
                **form.cleaned_data).first()

            if not keyword:
                keyword = form.save()
            elif app.keywords.contains(keyword):
                message = {
                    "text": f"Указанный ключ уже добавлен к приложению!", "success": False}
                return render(request, "apps/keywords/keyword_add.html", {"form": form, "app": app, "message": message})

            app.keywords.add(keyword)

            if not add_keyword_to_app_in_asoworld(app, keyword):
                app.keywords.remove(keyword)
                if keyword.app_set.count() == 0:  # type: ignore
                    keyword.delete()

                message = {
                    "text": f"Ошибка при добавлении ключа {keyword.name} региона {keyword.region} \
                            к приложению в ASO World. Пожалуйста, обратитесь к администратору!",
                    "success": False,
                }

                return render(request, "apps/keywords/keyword_add.html", {"form": form, "app": app, "message": message})

            if "_save" in request.POST:
                return HttpResponseRedirect(f"/apps_info/{app.id}/keywords/")

            message = {
                "text": f"Ключевое слово {keyword.name} региона {keyword.region} успешно добавлено!",
                "success": True,
            }

    else:
        form = Form()

    return render(request, "apps/keywords/keyword_add.html", {"form": form, "app": app, "message": message})


@check_app_permissions
@login_required
def remove_keyword_from_app(request, app_id: int, keyword_id: int):
    app = get_object_or_404(models.App, pk=app_id)
    keyword = get_object_or_404(models.Keyword, pk=keyword_id)
    message = {
        "text": f"Ключевое слово {keyword.name} региона {keyword.region} успешно отвязано от приложения!",
        "success": True,
    }

    if not app.keywords.contains(keyword):
        message = {
            "text": f"Ключевое слово {keyword.name} региона {keyword.region} не привязано к данному приложению!",
            "success": False,
        }
        return render(
            request, "apps/keywords/keyword_remove.html", {
                "app": app, "keyword": keyword, "message": message}
        )

    app.keywords.remove(keyword)
    return render(request, "apps/keywords/keyword_remove.html", {"app": app, "keyword": keyword, "message": message})
