from django.contrib.auth.decorators import login_required
from django.forms import modelform_factory
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
import json

from src.asoworld import add_app_to_asoworld, add_keyword_to_app_in_asoworld
from src.apps_state import check_app
from web.kwfinder import models


@login_required
def appsAnalytics(request):
    """ View for showing apps analytics page """
    apps = models.App.objects.all().order_by("-is_active", "num")
    return render(request, 'apps/apps_stats.html', {'apps': apps})


@login_required
def appAnalytics(request, app_id: int):
    try:
        app = models.App.objects.get(pk=app_id)
    except models.App.DoesNotExist:
        raise Http404("App does not exist")
    keywords = app.keywords.all().order_by("name")
    return render(request, 'apps/app_stats.html', {'app': app, "keywords": keywords})


@login_required
def consoleDataAdd(request, app_id: int):
    try:
        app = models.App.objects.get(pk=app_id)
    except models.App.DoesNotExist:
        raise Http404("App does not exist")

    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Data is not a valid json"}, status=400)

        try:
            data = data['data']

            for d in data:
                try:
                    keyword = models.Keyword.objects.get(id=d['keyword__id'])
                except models.Keyword.DoesNotExist:
                    continue

                console_data = models.ConsoleDailyData.objects.filter(
                    app=app,
                    keyword=keyword,
                    date=d['date']
                ).first()

                if not console_data:
                    console_data = models.ConsoleDailyData(
                        app=app,
                        keyword=keyword,
                        date=d['date']
                    )

                console_data.views = d['views']
                console_data.installs = d['installs']
                console_data.save()

        except (ValueError, KeyError):
            return JsonResponse({"error": "Data is not valid"}, status=400)

        return JsonResponse({"success": True})

    keywords = app.keywords.all()
    return render(request, 'apps/console_data_add.html', {'app': app, "keywords": keywords})


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
                return render(request, "apps/app_add.html",
                              {"form": form,
                               "error": "Ошибка при добавлении приложения в ASO World. \
                                Пожалуйста, обратитесь к администратору!"})
            check_app(app)
            return HttpResponseRedirect(f'/apps_info/{app.id}/')
    else:
        form = Form()

    return render(request, "apps/app_add.html", {"form": form})


@login_required
def app_keywords(request, app_id: int):
    try:
        app = models.App.objects.get(pk=app_id)
    except models.App.DoesNotExist:
        raise Http404("App does not exist")
        # return JsonResponse({"error": "App does not exist"}, status=404)

    keywords = app.keywords.all().order_by("region", "name")
    return render(request, 'apps/keywords.html', {'app': app, "keywords": keywords})


@login_required
def add_keyword_to_app(request, app_id: int):
    try:
        app = models.App.objects.get(pk=app_id)
    except models.App.DoesNotExist:
        raise Http404("App does not exist")

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
                    "text": f"Указанный ключ уже добавлен к приложению!",
                    "success": False
                }
                return render(request, "apps/keyword_add.html",
                              {"form": form, "app": app,
                               "message": message})

            app.keywords.add(keyword)

            if not add_keyword_to_app_in_asoworld(app, keyword):
                app.keywords.remove(keyword)
                if keyword.app_set.count() == 0:  # type: ignore
                    keyword.delete()

                message = {
                    "text": f"Ошибка при добавлении ключа {keyword.name} региона {keyword.region} \
                            к приложению в ASO World. Пожалуйста, обратитесь к администратору!",
                    "success": False
                }

                return render(request, "apps/keyword_add.html",
                              {"form": form, "app": app,
                               "message": message})

            if "_save" in request.POST:
                return HttpResponseRedirect(f'/apps_info/{app.id}/keywords/')

            message = {
                "text": f"Ключевое слово {keyword.name} региона {keyword.region} успешно добавлено!",
                "success": True
            }

    else:
        form = Form()

    return render(request, "apps/keyword_add.html", {"form": form, "app": app, "message": message})
