from django.contrib import admin
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import path

from . import forms
from . import models


@admin.register(models.AppPlatform)
class AppPlatformAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(models.AppType)
class AppTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'asoworld_region')


@admin.register(models.App)
class AppAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'num', 'app_type', 'is_active')
    list_select_related = ('app_type',)
    search_fields = ('name', 'num',)
    list_filter = ('is_active',)


@admin.register(models.Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'app_type')
    list_select_related = ('app_type',)
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
    list_select_related = ('app_type',)
    list_filter = ('app_type',)


@admin.register(models.AppPositionScriptRunData)
class AppPositionScriptRunDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'run', 'keyword', 'app', 'position')
    list_select_related = ('run', 'app', 'keyword')
    search_fields = ('keyword__name',)
    list_filter = ('run', 'app', 'keyword',)


@admin.register(models.DailyAggregatedPositionData)
class DailyAggregatedPositionDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'keyword', 'app', 'position')
    list_select_related = ('app', 'keyword')
    search_fields = ('keyword__name',)
    list_filter = ('date', 'app')


@admin.register(models.KeitaroDailyAppData)
class KeitaroDailyAppDataAdmin(admin.ModelAdmin):
    list_display = ('date', 'app', 'unique_users_count',
                    'conversions_count', 'sales_count', 'revenue',)
    list_select_related = ('app',)
    search_fields = ('app__name',)
    list_filter = ('date', 'app')


@admin.register(models.ASOWorldRegion)
class ASOWorldRegionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name',)
    search_fields = ('code', 'name',)

    def has_add_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False
