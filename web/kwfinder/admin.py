from django.contrib import admin

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
    search_fields = ('keyword',)
    list_filter = ('date', 'app')
