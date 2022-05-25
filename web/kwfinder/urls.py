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
# router.register('', views.AppView, basename='apps')

urlpatterns = [
    path('',
         views.dailyAnalytics,
         name='analytics'),
]
urlpatterns += router.urls
