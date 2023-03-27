from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register('apps', views.AppView, basename='apps')
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
#     path('apps_info/',
#          views.appsAnalytics,
#          name='apps_info'),
#     path('apps_info/<int:app_id>/',
#          views.appAnalytics,
#          name='app_info'),
#     path('apps_info/<int:app_id>/console_data/',
#          views.consoleDataAdd,
#          name='console_data_add'),
#     path('apps_info/<int:app_id>/keywords/',
#          views.app_keywords,
#          name='app_keywords'),
#     path('apps_info/<int:app_id>/keywords/add/',
#          views.add_keyword_to_app,
#          name='app_keywords_add'),
#     path('apps_info/add/',
#          views.add_app,
#          name='apps_info_add'),
]
urlpatterns += router.urls
