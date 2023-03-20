from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register('apps', views.AppView, basename='apps')
router.register('app_types', views.AppTypeView, basename='app_types')
router.register('app_platforms', views.AppPlatformView,
                basename='app_platforms')
router.register('keywords', views.KeywordView, basename='keywords')
router.register('daily_data', views.DailyAggregatedDataView,
                basename='daily_data')
router.register('keitaro_data', views.KeitaroDailyAppDataView,
                basename='keitaro_data')
router.register('console_data', views.ConsoleDailyDataView,
                basename='console_data')
router.register('position_data',
                views.AppPositionScriptRunDataView, basename='position_data')
router.register('asoworld_data',
                views.ASOWorldOrderKeywordDataView, basename='asoworld_data')
# router.register('', views.AppView, basename='apps')

urlpatterns = [
    path('',
         views.dailyAnalytics,
         name='analytics'),
    path('apps_analytics',
         views.appsAnalytics,
         name='apps_analytics'),
    path('apps_analytics/<int:app_id>/',
         views.appAnalytics,
         name='app_analytics'),
    path('console_data_add/<int:app_id>/',
         views.consoleDataAdd,
         name='console_data_add'),
    path('console_data_add/<int:app_id>/save/',
         views.consoleDataAddSave,
         name='console_data_add_save'),
]
urlpatterns += router.urls
