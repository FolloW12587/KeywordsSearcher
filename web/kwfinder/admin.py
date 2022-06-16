from django.contrib import admin
from django.shortcuts import redirect, render
from django.urls import path

from . import forms
from . import models


@admin.register(models.AppPlatform)
class AppPlatformAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(models.AppType)
class AppTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(models.App)
class AppAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'platform', 'app_type')
    search_fields = ('name',)


@admin.register(models.Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'app_type')
    search_fields = ('name',)
    list_filter = ('app_type',)

    change_list_template = "kwfinder/keywords_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            form = forms.CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES["csv_file"]
                app_type_id = request.POST['app_type']
                app_type = models.AppType.objects.get(id=app_type_id)

                keywords = []
                for line in csv_file:
                    keyword = line.strip().decode("utf-8")
                    if keyword == '' or models.Keyword.objects.filter(name=keyword).count() > 0:
                        continue

                    keywords.append(models.Keyword(
                        name=keyword,
                        app_type=app_type
                    ))

                models.Keyword.objects.bulk_create(keywords)
                self.message_user(request, "Your csv file has been imported")
                return redirect("..")
        form = forms.CsvImportForm()
        payload = {"form": form}
        return render(
            request, "kwfinder/csv_import_form.html", payload
        )


@admin.register(models.AppPositionScriptRun)
class AppPositionScriptRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'app_type', 'started_at', 'ended_at')
    list_filter = ('app_type',)


@admin.register(models.AppPositionScriptRunData)
class AppPositionScriptRunDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'run', 'keyword', 'app', 'position')
    search_fields = ('keyword__name',)
    list_filter = ('run', 'app')


@admin.register(models.DailyAggregatedPositionData)
class DailyAggregatedPositionDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'keyword', 'app', 'position')
    search_fields = ('keyword__name',)
    list_filter = ('date', 'app')
