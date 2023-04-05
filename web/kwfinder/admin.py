from django.contrib import admin
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import path
# from rest_framework.authtoken.models import TokenProxy

from . import forms
from . import models


# admin.site.unregister(TokenProxy)


@admin.register(models.AppPlatform)
class AppPlatformAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(models.App)
class AppAdmin(admin.ModelAdmin):
    list_display = ('name', 'num', 'region', 'is_active')
    list_select_related = ('region',)
    search_fields = ('name', 'num',)
    list_filter = ('is_active',)
    actions = ('unban',)
    filter_horizontal = ('keywords',)

    @admin.action(description="Отметить как активное")
    def unban(self, request, queryset):
        queryset.update(is_active=True)


@admin.register(models.Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'region')
    list_select_related = ('region',)
    search_fields = ('name',)
    list_filter = ('region',)

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
                region_id = request.POST['region']
                app_id = request.POST['app']

                region = models.ASOWorldRegion.objects.get(id=region_id)
                app = models.App.objects.get(id=app_id)

                for line in csv_file:
                    keyword = line.strip().decode("utf-8")
                    if keyword == '':
                        continue

                    keyword_db = models.Keyword.objects\
                        .filter(name=keyword).first()

                    if keyword_db == None:
                        keyword_db = models.Keyword.objects.create(
                            name=keyword, region=region)
                        app.keywords.add(keyword_db)
                        continue

                    if not app.keywords.contains(keyword):
                        app.keywords.add(keyword_db)

                self.message_user(request, "Your csv file has been imported.")
                return redirect("..")
        form = forms.CsvImportForm()
        payload = {"form": form}
        return render(
            request, "kwfinder/csv_import_form.html", payload
        )


@admin.register(models.AppPositionScriptRun)
class AppPositionScriptRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'started_at', 'ended_at')


class AppInline(admin.TabularInline):
    fields = ('num', 'name', 'region', 'is_active')
    model = models.App

    def has_add_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


@admin.register(models.AppGroup)
class AppGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    inlines = (AppInline,)


@admin.register(models.AppPositionScriptRunData)
class AppPositionScriptRunDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'run', 'keyword', 'app', 'position')
    list_select_related = ('run', 'app', 'keyword')
    search_fields = ('keyword__name',)
    list_filter = ('app', 'keyword',)


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


@admin.register(models.ConsoleDailyData)
class ConsoleDailyDataAdmin(admin.ModelAdmin):
    list_display = ('date', 'app', 'keyword',
                    'views', 'installs', 'conversion',)
    list_select_related = ('app', 'keyword')
    search_fields = ('app__name', 'keyword__name',)
    list_filter = ('date', 'app')


@admin.register(models.ASOWorldRegion)
class ASOWorldRegionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name',)
    search_fields = ('code', 'name',)

    def has_add_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


class ASOWorldOrderKeywordDataInline(admin.TabularInline):
    model = models.ASOWorldOrderKeywordData

    def has_add_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


@admin.register(models.ASOWorldOrder)
class ASOWorldOrderAdmin(admin.ModelAdmin):
    list_display = ("asoworld_id", "app", "submit_type",
                    "state", "price", "started_at")
    list_select_related = ('app',)
    list_filter = ('submit_type', 'state', "install_type")
    search_fields = ("asoworld_id",)
    inlines = (ASOWorldOrderKeywordDataInline,)

    # def has_add_permission(self, request, obj=None) -> bool:
    #     return False

    # def has_delete_permission(self, request, obj=None) -> bool:
    #     return False

    # def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
    #     return False


@admin.register(models.ASOWorldOrderKeywordData)
class ASOWorldOrderKeywordDataAdmin(admin.ModelAdmin):
    list_display = ("order", "keyword", "installs", "date")
    list_select_related = ('order', "keyword")
    search_fields = ('keyword__name', 'order__asoworld_id')

    def has_add_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False
